# -*- coding: utf-8 -*-
"""
Módulo utilitário para funções de interpolação RBF avançada.
"""

import numpy as np
from scipy.interpolate import Rbf, griddata
from scipy.spatial import cKDTree

# Import GDAL e OSR apenas se necessário em funções específicas
try:
    from osgeo import gdal, osr
except ImportError:
    gdal = None
    osr = None


def interpolate_rbf_advanced(points, values, grid_x, grid_y, function='thin_plate', 
                           smooth=0.1, max_neighbors=None, search_radius=None, 
                           extrapolation_method='constant', extrapolation_value=None, 
                           feedback=None):
    """
    Função avançada de interpolação RBF com controle de vizinhança e extrapolação.
    (Conteúdo migrado de legacy/rbf_interpolation_v2_claude.py)
    """
    if feedback:
        feedback.setProgressText("Preparando dados para interpolação...")
    
    # Normalizar coordenadas
    x_min, x_max = points[:, 0].min(), points[:, 0].max()
    y_min, y_max = points[:, 1].min(), points[:, 1].max()
    x_range = max(x_max - x_min, 1.0)
    y_range = max(y_max - y_min, 1.0)
    
    points_norm = np.column_stack([
        (points[:, 0] - x_min) / x_range,
        (points[:, 1] - y_min) / y_range
    ])
    
    # Criar grid normalizado
    X, Y = np.meshgrid(grid_x, grid_y)
    grid_points = np.column_stack([X.ravel(), Y.ravel()])
    grid_points_norm = np.column_stack([
        (grid_points[:, 0] - x_min) / x_range,
        (grid_points[:, 1] - y_min) / y_range
    ])
    
    # Construir árvore KD para busca eficiente de vizinhos
    if max_neighbors is not None or search_radius is not None:
        if feedback:
            feedback.setProgressText("Construindo árvore de busca espacial...")
        
        tree = cKDTree(points_norm)
        grid_shape = X.shape
        result_grid = np.full(grid_points.shape[0], np.nan)
        
        # Determinar raio de busca normalizado
        if search_radius is not None:
            # Normalizar o raio de busca
            search_radius_norm = search_radius / min(x_range, y_range)
        else:
            search_radius_norm = np.inf
        
        # Interpolar ponto por ponto usando vizinhança local
        total_points = len(grid_points_norm)
        
        for i, grid_point in enumerate(grid_points_norm):
            if feedback and i % 1000 == 0:
                progress = int((i / total_points) * 60) + 20  # 20-80% do progresso
                feedback.setProgress(progress)
                if feedback.isCanceled():
                    return None
            
            # Buscar vizinhos
            if max_neighbors is not None:
                distances, indices = tree.query(grid_point, k=min(max_neighbors, len(points_norm)))
            else:
                indices = tree.query_ball_point(grid_point, search_radius_norm)
                if len(indices) == 0:
                    continue
                distances = np.linalg.norm(points_norm[indices] - grid_point, axis=1)
            
            # Filtrar por raio se especificado
            if search_radius is not None:
                if isinstance(indices, (list, np.ndarray)):
                    valid_mask = distances <= search_radius_norm
                    indices = np.array(indices)[valid_mask]
                    distances = distances[valid_mask]
                else:
                    # Caso de um único vizinho
                    if distances > search_radius_norm:
                        continue
                    indices = [indices]
            
            # Verificar se temos pontos suficientes
            if len(indices) < 2:
                continue
            
            # Criar RBF local
            try:
                local_points = points_norm[indices]
                local_values = values[indices]
                
                if len(local_values) >= 2:  # Mínimo para RBF
                    rbf_local = Rbf(local_points[:, 0], local_points[:, 1], local_values,
                                  function=function, smooth=smooth)
                    result_grid[i] = rbf_local(grid_point[0], grid_point[1])
            except Exception as e:
                # Em caso de erro, usar interpolação linear local
                try:
                    local_points_orig = points[indices]
                    local_values = values[indices]
                    grid_point_orig = grid_points[i:i+1]
                    interp_val = griddata(local_points_orig, local_values, 
                                        grid_point_orig, method='linear')
                    if not np.isnan(interp_val[0]):
                        result_grid[i] = interp_val[0]
                except:
                    continue
        
        # Reshape para formato de grid
        result_grid = result_grid.reshape(grid_shape)
        
    else:
        # Interpolação global tradicional
        if feedback:
            feedback.setProgressText("Realizando interpolação RBF global...")
        
        try:
            rbf = Rbf(points_norm[:, 0], points_norm[:, 1], values, 
                     function=function, smooth=smooth)
            X_norm = (X - x_min) / x_range
            Y_norm = (Y - y_min) / y_range
            result_grid = rbf(X_norm, Y_norm)
        except Exception as e:
            if feedback:
                feedback.pushWarning(f"Erro no RBF global: {e}. Usando griddata.")
            result_grid = griddata(points, values, (X, Y), method='linear')
    
    # Tratamento de extrapolação
    if feedback:
        feedback.setProgressText("Aplicando tratamento de extrapolação...")
    
    if extrapolation_method != 'none':
        nan_mask = np.isnan(result_grid)
        
        if np.any(nan_mask):
            if extrapolation_method == 'constant':
                if extrapolation_value is not None:
                    result_grid[nan_mask] = extrapolation_value
                else:
                    # Usar média dos valores conhecidos
                    result_grid[nan_mask] = np.nanmean(values)
            
            elif extrapolation_method == 'nearest':
                # Usar vizinho mais próximo para extrapolação
                tree = cKDTree(points)
                nan_points = np.column_stack([X[nan_mask], Y[nan_mask]])
                _, nearest_indices = tree.query(nan_points)
                result_grid[nan_mask] = values[nearest_indices]
            
            elif extrapolation_method == 'linear':
                # Usar interpolação linear para extrapolação
                try:
                    linear_result = griddata(points, values, (X, Y), method='linear', 
                                           fill_value=np.nanmean(values))
                    result_grid[nan_mask] = linear_result[nan_mask]
                except:
                    # Fallback para valor constante
                    result_grid[nan_mask] = np.nanmean(values)
    
    # Aplicar clipping físico
    if not np.all(np.isnan(result_grid)):
        val_min, val_max = np.nanmin(values), np.nanmax(values)
        val_range = val_max - val_min
        if val_range > 0:
            result_grid = np.clip(result_grid, val_min - 0.2*val_range, val_max + 0.2*val_range)
    
    return result_grid
