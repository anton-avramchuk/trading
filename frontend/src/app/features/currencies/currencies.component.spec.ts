import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { CurrenciesComponent } from './currencies.component';
import { CurrenciesService } from '../../core/services/currencies.service';
import { Currency, CurrencyCreate } from '../../core/models/currency.model';

describe('CurrenciesComponent', () => {
  let component: CurrenciesComponent;
  let fixture: ComponentFixture<CurrenciesComponent>;
  let currenciesService: jasmine.SpyObj<CurrenciesService>;

  const mockCurrencies: Currency[] = [
    {
      id: 1,
      code: 'RUB',
      numeric_code: '643',
      name: 'Российский рубль',
      name_en: 'Russian Ruble',
      symbol: '₽',
      decimal_places: 2,
      is_active: 1,
      created_at: '2025-01-01T00:00:00Z'
    },
    {
      id: 2,
      code: 'USD',
      numeric_code: '840',
      name: 'Доллар США',
      name_en: 'US Dollar',
      symbol: '$',
      decimal_places: 2,
      is_active: 1,
      created_at: '2025-01-01T00:00:00Z'
    },
    {
      id: 3,
      code: 'BTC',
      name: 'Bitcoin',
      decimal_places: 8,
      is_active: 0,
      created_at: '2025-01-01T00:00:00Z'
    }
  ];

  beforeEach(async () => {
    const currenciesServiceSpy = jasmine.createSpyObj('CurrenciesService', [
      'getCurrencies',
      'getCurrency',
      'createCurrency',
      'updateCurrency',
      'deleteCurrency'
    ]);

    await TestBed.configureTestingModule({
      imports: [CurrenciesComponent],
      providers: [
        { provide: CurrenciesService, useValue: currenciesServiceSpy }
      ]
    }).compileComponents();

    currenciesService = TestBed.inject(CurrenciesService) as jasmine.SpyObj<CurrenciesService>;
    fixture = TestBed.createComponent(CurrenciesComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should load currencies on init', () => {
      currenciesService.getCurrencies.and.returnValue(of(mockCurrencies));

      fixture.detectChanges();

      expect(currenciesService.getCurrencies).toHaveBeenCalledWith(undefined);
      expect(component.currencies()).toEqual(mockCurrencies);
      expect(component.loading()).toBe(false);
      expect(component.error()).toBeNull();
    });

    it('should handle error on init', () => {
      const error = new Error('Network error');
      currenciesService.getCurrencies.and.returnValue(throwError(() => error));

      fixture.detectChanges();

      expect(component.currencies()).toEqual([]);
      expect(component.loading()).toBe(false);
      expect(component.error()).toBe('Network error');
    });
  });

  describe('loadCurrencies', () => {
    it('should load all currencies when showActiveOnly is false', () => {
      currenciesService.getCurrencies.and.returnValue(of(mockCurrencies));
      component.showActiveOnly = false;

      component.loadCurrencies();

      expect(currenciesService.getCurrencies).toHaveBeenCalledWith(undefined);
      expect(component.currencies()).toEqual(mockCurrencies);
      expect(component.loading()).toBe(false);
    });

    it('should load active currencies only when showActiveOnly is true', () => {
      const activeCurrencies = mockCurrencies.filter(c => c.is_active === 1);
      currenciesService.getCurrencies.and.returnValue(of(activeCurrencies));
      component.showActiveOnly = true;

      component.loadCurrencies();

      expect(currenciesService.getCurrencies).toHaveBeenCalledWith({ active_only: true });
      expect(component.currencies()).toEqual(activeCurrencies);
    });

    it('should set loading state correctly', () => {
      currenciesService.getCurrencies.and.returnValue(of(mockCurrencies));

      expect(component.loading()).toBe(false);

      component.loadCurrencies();

      // Loading should be set to false after subscription completes
      expect(component.loading()).toBe(false);
    });

    it('should handle error and set error message', () => {
      const errorMessage = 'Failed to fetch currencies';
      currenciesService.getCurrencies.and.returnValue(
        throwError(() => ({ message: errorMessage }))
      );

      component.loadCurrencies();

      expect(component.error()).toBe(errorMessage);
      expect(component.loading()).toBe(false);
    });

    it('should handle error without message', () => {
      currenciesService.getCurrencies.and.returnValue(
        throwError(() => ({}))
      );

      component.loadCurrencies();

      expect(component.error()).toBe('Не удалось загрузить валюты');
      expect(component.loading()).toBe(false);
    });
  });

  describe('showAddForm', () => {
    it('should show empty form for adding new currency', () => {
      component.showAddForm();

      expect(component.showForm()).toBe(true);
      expect(component.editingCurrency()).toBeNull();
      expect(component.formData.code).toBe('');
      expect(component.formData.name).toBe('');
      expect(component.formData.decimal_places).toBe(2);
      expect(component.formData.is_active_bool).toBe(true);
    });
  });

  describe('editCurrency', () => {
    it('should populate form with currency data for editing', () => {
      const currency = mockCurrencies[0];

      component.editCurrency(currency);

      expect(component.showForm()).toBe(true);
      expect(component.editingCurrency()).toEqual(currency);
      expect(component.formData.code).toBe(currency.code);
      expect(component.formData.name).toBe(currency.name);
      expect(component.formData.symbol).toBe(currency.symbol);
      expect(component.formData.decimal_places).toBe(currency.decimal_places);
      expect(component.formData.is_active_bool).toBe(true);
    });

    it('should set is_active_bool to false for inactive currency', () => {
      const inactiveCurrency = mockCurrencies[2];

      component.editCurrency(inactiveCurrency);

      expect(component.formData.is_active_bool).toBe(false);
    });
  });

  describe('saveCurrency', () => {
    it('should create new currency when not editing', () => {
      const newCurrency: CurrencyCreate = {
        code: 'EUR',
        numeric_code: '978',
        name: 'Евро',
        name_en: 'Euro',
        symbol: '€',
        decimal_places: 2,
        is_active: 1
      };

      component.formData = { ...newCurrency, is_active_bool: true };
      component.editingCurrency.set(null);

      const createdCurrency: Currency = { id: 4, ...newCurrency, created_at: '2025-01-01' } as Currency;
      currenciesService.createCurrency.and.returnValue(of(createdCurrency));
      currenciesService.getCurrencies.and.returnValue(of([...mockCurrencies, createdCurrency]));

      component.saveCurrency();

      expect(currenciesService.createCurrency).toHaveBeenCalledWith(newCurrency);
      expect(component.saving()).toBe(false);
      expect(component.showForm()).toBe(false);
    });

    it('should update existing currency when editing', () => {
      const currencyToEdit = mockCurrencies[0];
      const updatedData: CurrencyCreate = {
        code: currencyToEdit.code,
        numeric_code: currencyToEdit.numeric_code,
        name: 'Обновленное название',
        name_en: undefined,
        symbol: undefined,
        decimal_places: 2,
        is_active: 1
      };

      component.formData = { ...updatedData, is_active_bool: true };
      component.editingCurrency.set(currencyToEdit);

      currenciesService.updateCurrency.and.returnValue(of({ ...currencyToEdit, ...updatedData }));
      currenciesService.getCurrencies.and.returnValue(of(mockCurrencies));

      component.saveCurrency();

      expect(currenciesService.updateCurrency).toHaveBeenCalledWith(currencyToEdit.id, updatedData);
      expect(component.saving()).toBe(false);
      expect(component.showForm()).toBe(false);
    });

    it('should convert is_active_bool to is_active number', () => {
      const newCurrency: CurrencyCreate = {
        code: 'JPY',
        name: 'Японская йена',
        decimal_places: 0,
        is_active: 0
      };

      component.formData = { ...newCurrency, is_active_bool: false };
      component.editingCurrency.set(null);

      const createdCurrency: Currency = { id: 5, ...newCurrency, created_at: '2025-01-01' } as Currency;
      currenciesService.createCurrency.and.returnValue(of(createdCurrency));
      currenciesService.getCurrencies.and.returnValue(of(mockCurrencies));

      component.saveCurrency();

      const createCall = currenciesService.createCurrency.calls.mostRecent();
      expect(createCall.args[0].is_active).toBe(0);
    });

    it('should handle create error', () => {
      spyOn(window, 'alert');
      component.formData = {
        code: 'EUR',
        name: 'Euro',
        decimal_places: 2,
        is_active: 1,
        is_active_bool: true
      };
      component.editingCurrency.set(null);

      const errorResponse = { error: { detail: 'Currency already exists' } };
      currenciesService.createCurrency.and.returnValue(throwError(() => errorResponse));

      component.saveCurrency();

      expect(component.saving()).toBe(false);
      expect(window.alert).toHaveBeenCalledWith('Ошибка: Currency already exists');
    });

    it('should handle update error', () => {
      spyOn(window, 'alert');
      const currency = mockCurrencies[0];
      component.formData = {
        code: currency.code,
        name: 'Updated',
        decimal_places: 2,
        is_active: 1,
        is_active_bool: true
      };
      component.editingCurrency.set(currency);

      currenciesService.updateCurrency.and.returnValue(throwError(() => new Error('Update failed')));

      component.saveCurrency();

      expect(component.saving()).toBe(false);
      expect(window.alert).toHaveBeenCalledWith('Ошибка: Update failed');
    });
  });

  describe('cancelEdit', () => {
    it('should hide form and clear editing currency', () => {
      component.showForm.set(true);
      component.editingCurrency.set(mockCurrencies[0]);

      component.cancelEdit();

      expect(component.showForm()).toBe(false);
      expect(component.editingCurrency()).toBeNull();
    });
  });

  describe('confirmDelete', () => {
    it('should set deletingCurrency to show confirmation dialog', () => {
      const currency = mockCurrencies[0];

      component.confirmDelete(currency);

      expect(component.deletingCurrency()).toEqual(currency);
    });
  });

  describe('deleteCurrency', () => {
    it('should delete currency and reload list', () => {
      const currency = mockCurrencies[0];
      component.deletingCurrency.set(currency);

      currenciesService.deleteCurrency.and.returnValue(of(undefined));
      currenciesService.getCurrencies.and.returnValue(of(mockCurrencies.slice(1)));

      component.deleteCurrency();

      expect(currenciesService.deleteCurrency).toHaveBeenCalledWith(currency.id);
      expect(component.deletingCurrency()).toBeNull();
    });

    it('should not delete if deletingCurrency is null', () => {
      component.deletingCurrency.set(null);

      component.deleteCurrency();

      expect(currenciesService.deleteCurrency).not.toHaveBeenCalled();
    });

    it('should handle delete error', () => {
      spyOn(window, 'alert');
      const currency = mockCurrencies[0];
      component.deletingCurrency.set(currency);

      const errorResponse = { error: { detail: 'Currency is in use' } };
      currenciesService.deleteCurrency.and.returnValue(throwError(() => errorResponse));

      component.deleteCurrency();

      expect(component.deletingCurrency()).toBeNull();
      expect(window.alert).toHaveBeenCalledWith('Ошибка удаления: Currency is in use');
    });
  });

  describe('cancelDelete', () => {
    it('should clear deletingCurrency and hide confirmation dialog', () => {
      component.deletingCurrency.set(mockCurrencies[0]);

      component.cancelDelete();

      expect(component.deletingCurrency()).toBeNull();
    });
  });

  describe('getEmptyFormData', () => {
    it('should return empty form data with default values', () => {
      const emptyData = component['getEmptyFormData']();

      expect(emptyData.code).toBe('');
      expect(emptyData.name).toBe('');
      expect(emptyData.numeric_code).toBeUndefined();
      expect(emptyData.name_en).toBeUndefined();
      expect(emptyData.symbol).toBeUndefined();
      expect(emptyData.decimal_places).toBe(2);
      expect(emptyData.is_active).toBe(1);
      expect(emptyData.is_active_bool).toBe(true);
    });
  });
});
