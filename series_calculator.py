import math

class SeriesCalculator:
    @staticmethod
    def factorial(n):
        """Calcula el factorial de n."""
        if n == 0 or n == 1:
            return 1
        else:
            return n * SeriesCalculator.factorial(n-1)
    
    @staticmethod
    def sin_series(x, n_terms):
        """
        Calcula la aproximación de sen(x) usando series de Taylor.
        x: valor donde calcular la función
        n_terms: número de términos a usar en la serie
        """
        result = 0
        for n in range(n_terms):
            term = ((-1) ** n) * (x ** (2*n + 1)) / SeriesCalculator.factorial(2*n + 1)
            result += term
        
        # Calculamos el valor exacto y el error
        exact_value = math.sin(x)
        error = abs(exact_value - result)
        
        return result, exact_value, error
    
    @staticmethod
    def cos_series(x, n_terms):
        """
        Calcula la aproximación de cos(x) usando series de Taylor.
        x: valor donde calcular la función
        n_terms: número de términos a usar en la serie
        """
        result = 0
        for n in range(n_terms):
            term = ((-1) ** n) * (x ** (2*n)) / SeriesCalculator.factorial(2*n)
            result += term
        
        # Calculamos el valor exacto y el error
        exact_value = math.cos(x)
        error = abs(exact_value - result)
        
        return result, exact_value, error
    
    @staticmethod
    def tan_series(x, n_terms):
        """
        Calcula la aproximación de tan(x) usando las series de seno y coseno.
        x: valor donde calcular la función
        n_terms: número de términos a usar en cada serie
        """
        # Comprobamos que x no esté en π/2 + kπ
        if abs(math.cos(x)) < 1e-10:
            raise ValueError("El valor de x está demasiado cerca de una singularidad de tan(x)")
        
        sin_approx, _, _ = SeriesCalculator.sin_series(x, n_terms)
        cos_approx, _, _ = SeriesCalculator.cos_series(x, n_terms)
        
        if abs(cos_approx) < 1e-10:
            # Evitamos división por números muy pequeños
            result = float('inf')
        else:
            result = sin_approx / cos_approx
        
        # Calculamos el valor exacto y el error
        exact_value = math.tan(x)
        error = abs(exact_value - result)
        
        return result, exact_value, error
    
    @staticmethod
    def calculate_series(series_type, x, n_terms):
        """
        Interfaz para calcular cualquier tipo de serie.
        series_type: 'sin', 'cos', 'tan'
        x: valor donde calcular
        n_terms: número de términos
        """
        if series_type.lower() == 'sin':
            return SeriesCalculator.sin_series(x, n_terms)
        elif series_type.lower() == 'cos':
            return SeriesCalculator.cos_series(x, n_terms)
        elif series_type.lower() == 'tan':
            return SeriesCalculator.tan_series(x, n_terms)
        else:
            raise ValueError(f"Tipo de serie no soportado: {series_type}")
