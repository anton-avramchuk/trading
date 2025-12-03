import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LoaderComponent } from './loader.component';

describe('LoaderComponent', () => {
  let component: LoaderComponent;
  let fixture: ComponentFixture<LoaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoaderComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(LoaderComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display default message', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Загрузка...');
  });

  it('should display custom message', () => {
    fixture.componentRef.setInput('message', 'Загружаем данные...');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Загружаем данные...');
  });

  it('should apply overlay class when overlay is true', () => {
    fixture.componentRef.setInput('overlay', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.loader-container');
    expect(container?.classList.contains('overlay')).toBe(true);
  });

  it('should not apply overlay class when overlay is false', () => {
    fixture.componentRef.setInput('overlay', false);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.loader-container');
    expect(container?.classList.contains('overlay')).toBe(false);
  });

  it('should set custom size', () => {
    fixture.componentRef.setInput('size', 60);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const spinner = compiled.querySelector('.spinner') as HTMLElement;
    expect(spinner.style.width).toBe('60px');
    expect(spinner.style.height).toBe('60px');
  });

  it('should have spinner element', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const spinner = compiled.querySelector('.spinner-border');
    expect(spinner).toBeTruthy();
  });
});
