import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { CountriesComponent } from './countries.component';
import { CountriesService } from '../../core/services/countries.service';
import { Country, CountryCreate } from '../../core/models/country.model';

describe('CountriesComponent', () => {
  let component: CountriesComponent;
  let fixture: ComponentFixture<CountriesComponent>;
  let countriesService: jasmine.SpyObj<CountriesService>;

  const mockCountries: Country[] = [
    {
      id: 1,
      code: 'RU',
      code3: 'RUS',
      name: 'Россия',
      name_en: 'Russia',
      region: 'Europe',
      is_active: 1,
      created_at: '2025-01-01T00:00:00Z'
    },
    {
      id: 2,
      code: 'US',
      code3: 'USA',
      name: 'США',
      name_en: 'United States',
      region: 'Americas',
      is_active: 1,
      created_at: '2025-01-01T00:00:00Z'
    },
    {
      id: 3,
      code: 'CN',
      code3: 'CHN',
      name: 'Китай',
      name_en: 'China',
      region: 'Asia',
      is_active: 0,
      created_at: '2025-01-01T00:00:00Z'
    }
  ];

  beforeEach(async () => {
    const countriesServiceSpy = jasmine.createSpyObj('CountriesService', [
      'getCountries',
      'getCountry',
      'getCountryByCode',
      'createCountry',
      'updateCountry',
      'deleteCountry'
    ]);

    await TestBed.configureTestingModule({
      imports: [CountriesComponent],
      providers: [
        { provide: CountriesService, useValue: countriesServiceSpy }
      ]
    }).compileComponents();

    countriesService = TestBed.inject(CountriesService) as jasmine.SpyObj<CountriesService>;
    fixture = TestBed.createComponent(CountriesComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    it('should load countries on init', () => {
      countriesService.getCountries.and.returnValue(of(mockCountries));

      fixture.detectChanges();

      expect(countriesService.getCountries).toHaveBeenCalledWith(undefined);
      expect(component.countries()).toEqual(mockCountries);
      expect(component.loading()).toBe(false);
      expect(component.error()).toBeNull();
    });

    it('should handle error on init', () => {
      const error = new Error('Network error');
      countriesService.getCountries.and.returnValue(throwError(() => error));

      fixture.detectChanges();

      expect(component.countries()).toEqual([]);
      expect(component.loading()).toBe(false);
      expect(component.error()).toBe('Network error');
    });
  });

  describe('loadCountries', () => {
    it('should load all countries when no filters applied', () => {
      countriesService.getCountries.and.returnValue(of(mockCountries));
      component.showActiveOnly = false;
      component.filterRegion = '';

      component.loadCountries();

      expect(countriesService.getCountries).toHaveBeenCalledWith(undefined);
      expect(component.countries()).toEqual(mockCountries);
      expect(component.loading()).toBe(false);
    });

    it('should load active countries only when showActiveOnly is true', () => {
      const activeCountries = mockCountries.filter(c => c.is_active === 1);
      countriesService.getCountries.and.returnValue(of(activeCountries));
      component.showActiveOnly = true;
      component.filterRegion = '';

      component.loadCountries();

      expect(countriesService.getCountries).toHaveBeenCalledWith({ active_only: true });
      expect(component.countries()).toEqual(activeCountries);
    });

    it('should load countries filtered by region', () => {
      const europeCountries = mockCountries.filter(c => c.region === 'Europe');
      countriesService.getCountries.and.returnValue(of(europeCountries));
      component.showActiveOnly = false;
      component.filterRegion = 'Europe';

      component.loadCountries();

      expect(countriesService.getCountries).toHaveBeenCalledWith({ region: 'Europe' });
      expect(component.countries()).toEqual(europeCountries);
    });

    it('should load countries with both filters active', () => {
      const filteredCountries = mockCountries.filter(c => c.is_active === 1 && c.region === 'Europe');
      countriesService.getCountries.and.returnValue(of(filteredCountries));
      component.showActiveOnly = true;
      component.filterRegion = 'Europe';

      component.loadCountries();

      expect(countriesService.getCountries).toHaveBeenCalledWith({ active_only: true, region: 'Europe' });
      expect(component.countries()).toEqual(filteredCountries);
    });

    it('should set loading state correctly', () => {
      countriesService.getCountries.and.returnValue(of(mockCountries));

      expect(component.loading()).toBe(false);

      component.loadCountries();

      // Loading should be set to false after subscription completes
      expect(component.loading()).toBe(false);
    });

    it('should handle error and set error message', () => {
      const errorMessage = 'Failed to fetch countries';
      countriesService.getCountries.and.returnValue(
        throwError(() => ({ message: errorMessage }))
      );

      component.loadCountries();

      expect(component.error()).toBe(errorMessage);
      expect(component.loading()).toBe(false);
    });

    it('should handle error without message', () => {
      countriesService.getCountries.and.returnValue(
        throwError(() => ({}))
      );

      component.loadCountries();

      expect(component.error()).toBe('Не удалось загрузить страны');
      expect(component.loading()).toBe(false);
    });
  });

  describe('showAddForm', () => {
    it('should show empty form for adding new country', () => {
      component.showAddForm();

      expect(component.showForm()).toBe(true);
      expect(component.editingCountry()).toBeNull();
      expect(component.formData.code).toBe('');
      expect(component.formData.name).toBe('');
      expect(component.formData.is_active_bool).toBe(true);
    });
  });

  describe('editCountry', () => {
    it('should populate form with country data for editing', () => {
      const country = mockCountries[0];

      component.editCountry(country);

      expect(component.showForm()).toBe(true);
      expect(component.editingCountry()).toEqual(country);
      expect(component.formData.code).toBe(country.code);
      expect(component.formData.code3).toBe(country.code3);
      expect(component.formData.name).toBe(country.name);
      expect(component.formData.name_en).toBe(country.name_en);
      expect(component.formData.region).toBe(country.region);
      expect(component.formData.is_active_bool).toBe(true);
    });

    it('should set is_active_bool to false for inactive country', () => {
      const inactiveCountry = mockCountries[2];

      component.editCountry(inactiveCountry);

      expect(component.formData.is_active_bool).toBe(false);
    });
  });

  describe('saveCountry', () => {
    it('should create new country when not editing', () => {
      const newCountry: CountryCreate = {
        code: 'DE',
        code3: 'DEU',
        name: 'Германия',
        name_en: 'Germany',
        region: 'Europe',
        is_active: 1
      };

      component.formData = { ...newCountry, is_active_bool: true };
      component.editingCountry.set(null);

      const createdCountry: Country = { id: 4, ...newCountry, created_at: '2025-01-01' } as Country;
      countriesService.createCountry.and.returnValue(of(createdCountry));
      countriesService.getCountries.and.returnValue(of([...mockCountries, createdCountry]));

      component.saveCountry();

      expect(countriesService.createCountry).toHaveBeenCalledWith(newCountry);
      expect(component.saving()).toBe(false);
      expect(component.showForm()).toBe(false);
    });

    it('should update existing country when editing', () => {
      const countryToEdit = mockCountries[0];
      const updatedData: CountryCreate = {
        code: countryToEdit.code,
        code3: countryToEdit.code3,
        name: 'Обновленное название',
        name_en: 'Updated name',
        region: 'Europe',
        is_active: 1
      };

      component.formData = { ...updatedData, is_active_bool: true };
      component.editingCountry.set(countryToEdit);

      countriesService.updateCountry.and.returnValue(of({ ...countryToEdit, ...updatedData }));
      countriesService.getCountries.and.returnValue(of(mockCountries));

      component.saveCountry();

      expect(countriesService.updateCountry).toHaveBeenCalledWith(countryToEdit.id, updatedData);
      expect(component.saving()).toBe(false);
      expect(component.showForm()).toBe(false);
    });

    it('should convert is_active_bool to is_active number', () => {
      const newCountry: CountryCreate = {
        code: 'FR',
        code3: 'FRA',
        name: 'Франция',
        region: 'Europe',
        is_active: 0
      };

      component.formData = { ...newCountry, is_active_bool: false };
      component.editingCountry.set(null);

      const createdCountry: Country = { id: 5, ...newCountry, created_at: '2025-01-01' } as Country;
      countriesService.createCountry.and.returnValue(of(createdCountry));
      countriesService.getCountries.and.returnValue(of(mockCountries));

      component.saveCountry();

      const createCall = countriesService.createCountry.calls.mostRecent();
      expect(createCall.args[0].is_active).toBe(0);
    });

    it('should handle create error', () => {
      spyOn(window, 'alert');
      component.formData = {
        code: 'DE',
        name: 'Germany',
        is_active: 1,
        is_active_bool: true
      };
      component.editingCountry.set(null);

      const errorResponse = { error: { detail: 'Country already exists' } };
      countriesService.createCountry.and.returnValue(throwError(() => errorResponse));

      component.saveCountry();

      expect(component.saving()).toBe(false);
      expect(window.alert).toHaveBeenCalledWith('Ошибка: Country already exists');
    });

    it('should handle update error', () => {
      spyOn(window, 'alert');
      const country = mockCountries[0];
      component.formData = {
        code: country.code,
        name: 'Updated',
        is_active: 1,
        is_active_bool: true
      };
      component.editingCountry.set(country);

      countriesService.updateCountry.and.returnValue(throwError(() => new Error('Update failed')));

      component.saveCountry();

      expect(component.saving()).toBe(false);
      expect(window.alert).toHaveBeenCalledWith('Ошибка: Update failed');
    });
  });

  describe('cancelEdit', () => {
    it('should hide form and clear editing country', () => {
      component.showForm.set(true);
      component.editingCountry.set(mockCountries[0]);

      component.cancelEdit();

      expect(component.showForm()).toBe(false);
      expect(component.editingCountry()).toBeNull();
    });
  });

  describe('confirmDelete', () => {
    it('should set deletingCountry to show confirmation dialog', () => {
      const country = mockCountries[0];

      component.confirmDelete(country);

      expect(component.deletingCountry()).toEqual(country);
    });
  });

  describe('deleteCountry', () => {
    it('should delete country and reload list', () => {
      const country = mockCountries[0];
      component.deletingCountry.set(country);

      countriesService.deleteCountry.and.returnValue(of(undefined));
      countriesService.getCountries.and.returnValue(of(mockCountries.slice(1)));

      component.deleteCountry();

      expect(countriesService.deleteCountry).toHaveBeenCalledWith(country.id);
      expect(component.deletingCountry()).toBeNull();
    });

    it('should not delete if deletingCountry is null', () => {
      component.deletingCountry.set(null);

      component.deleteCountry();

      expect(countriesService.deleteCountry).not.toHaveBeenCalled();
    });

    it('should handle delete error', () => {
      spyOn(window, 'alert');
      const country = mockCountries[0];
      component.deletingCountry.set(country);

      const errorResponse = { error: { detail: 'Country is in use' } };
      countriesService.deleteCountry.and.returnValue(throwError(() => errorResponse));

      component.deleteCountry();

      expect(component.deletingCountry()).toBeNull();
      expect(window.alert).toHaveBeenCalledWith('Ошибка удаления: Country is in use');
    });
  });

  describe('cancelDelete', () => {
    it('should clear deletingCountry and hide confirmation dialog', () => {
      component.deletingCountry.set(mockCountries[0]);

      component.cancelDelete();

      expect(component.deletingCountry()).toBeNull();
    });
  });

  describe('getEmptyFormData', () => {
    it('should return empty form data with default values', () => {
      const emptyData = component['getEmptyFormData']();

      expect(emptyData.code).toBe('');
      expect(emptyData.name).toBe('');
      expect(emptyData.code3).toBeUndefined();
      expect(emptyData.name_en).toBeUndefined();
      expect(emptyData.region).toBeUndefined();
      expect(emptyData.is_active).toBe(1);
      expect(emptyData.is_active_bool).toBe(true);
    });
  });
});
