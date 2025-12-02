import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';
import { inject } from '@angular/core';

/**
 * Interceptor для обработки HTTP ошибок
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'Произошла неизвестная ошибка';

      if (error.error instanceof ErrorEvent) {
        // Клиентская ошибка
        errorMessage = `Ошибка: ${error.error.message}`;
        console.error('Client-side error:', error.error.message);
      } else {
        // Серверная ошибка
        console.error(`Server-side error: ${error.status}`, error.error);

        switch (error.status) {
          case 400:
            errorMessage = error.error?.detail || 'Неверный запрос';
            break;
          case 401:
            errorMessage = 'Необходима авторизация';
            break;
          case 403:
            errorMessage = 'Доступ запрещён';
            break;
          case 404:
            errorMessage = error.error?.detail || 'Ресурс не найден';
            break;
          case 422:
            // Validation error от FastAPI
            if (error.error?.detail) {
              if (Array.isArray(error.error.detail)) {
                const validationErrors = error.error.detail
                  .map((err: any) => `${err.loc?.join('.') || 'field'}: ${err.msg}`)
                  .join('; ');
                errorMessage = `Ошибка валидации: ${validationErrors}`;
              } else {
                errorMessage = error.error.detail;
              }
            } else {
              errorMessage = 'Ошибка валидации данных';
            }
            break;
          case 500:
            errorMessage = 'Внутренняя ошибка сервера';
            break;
          case 503:
            errorMessage = 'Сервис временно недоступен';
            break;
          default:
            errorMessage = error.error?.detail || `Ошибка: ${error.status} ${error.statusText}`;
        }
      }

      // Здесь можно добавить показ уведомлений пользователю
      // например через toast service

      return throwError(() => ({
        message: errorMessage,
        status: error.status,
        originalError: error
      }));
    })
  );
};
