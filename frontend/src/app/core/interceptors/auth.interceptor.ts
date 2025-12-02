import { HttpInterceptorFn } from '@angular/common/http';

/**
 * Interceptor для добавления токена авторизации к запросам
 *
 * На данный момент авторизация не используется,
 * но interceptor подготовлен для будущего расширения
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // Проверяем, нужно ли добавлять токен
  // (не добавляем для публичных endpoints)
  if (shouldSkipAuth(req.url)) {
    return next(req);
  }

  // Получаем токен из localStorage (или другого хранилища)
  const token = getAuthToken();

  // Если токен есть, клонируем запрос и добавляем заголовок
  if (token) {
    const clonedRequest = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(clonedRequest);
  }

  return next(req);
};

/**
 * Проверяет, нужно ли пропустить добавление токена для этого URL
 */
function shouldSkipAuth(url: string): boolean {
  const publicEndpoints = [
    '/health',
    '/login',
    '/register'
  ];

  return publicEndpoints.some(endpoint => url.includes(endpoint));
}

/**
 * Получает токен авторизации из хранилища
 */
function getAuthToken(): string | null {
  // В будущем здесь будет логика получения токена
  // Например: return localStorage.getItem('auth_token');
  return null;
}
