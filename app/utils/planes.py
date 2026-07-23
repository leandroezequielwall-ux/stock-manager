PLANES_LIMITES = {
    'Starter': {
        'max_usuarios': 2,
        'max_productos': 100,
        'max_sucursales': 1,
        'api_acceso': False,
        'reportes_avanzados': False
    },
    'Pro': {
        'max_usuarios': 10,
        'max_productos': 1500,
        'max_sucursales': 3,
        'api_acceso': True,
        'reportes_avanzados': True
    },
    'Enterprise': {
        'max_usuarios': float('inf'), # Ilimitado
        'max_productos': float('inf'),
        'max_sucursales': float('inf'),
        'api_acceso': True,
        'reportes_avanzados': True
    }
}
