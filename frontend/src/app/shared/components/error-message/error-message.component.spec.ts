import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ErrorMessageComponent } from './error-message.component';

describe('ErrorMessageComponent', () => {
  let component: ErrorMessageComponent;
  let fixture: ComponentFixture<ErrorMessageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ErrorMessageComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ErrorMessageComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display default title and message', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.error-title')?.textContent).toContain('Ошибка');
    expect(compiled.querySelector('.error-message')?.textContent).toContain('Произошла неизвестная ошибка');
  });

  it('should display custom title and message', () => {
    fixture.componentRef.setInput('title', 'Ошибка загрузки');
    fixture.componentRef.setInput('message', 'Не удалось загрузить данные');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.error-title')?.textContent).toContain('Ошибка загрузки');
    expect(compiled.querySelector('.error-message')?.textContent).toContain('Не удалось загрузить данные');
  });

  it('should display details when provided', () => {
    fixture.componentRef.setInput('details', 'Stack trace here');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const details = compiled.querySelector('.error-details');
    expect(details).toBeTruthy();
    expect(details?.textContent).toContain('Stack trace here');
  });

  it('should not display details when not provided', () => {
    fixture.componentRef.setInput('details', '');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const details = compiled.querySelector('.error-details');
    expect(details).toBeFalsy();
  });

  it('should apply error type class', () => {
    fixture.componentRef.setInput('type', 'error');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.error-container');
    expect(container?.classList.contains('error-error')).toBe(true);
  });

  it('should apply warning type class', () => {
    fixture.componentRef.setInput('type', 'warning');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.error-container');
    expect(container?.classList.contains('error-warning')).toBe(true);
  });

  it('should show retry button when showRetry is true', () => {
    fixture.componentRef.setInput('showRetry', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const retryBtn = compiled.querySelector('.btn-retry');
    expect(retryBtn).toBeTruthy();
  });

  it('should hide retry button when showRetry is false', () => {
    fixture.componentRef.setInput('showRetry', false);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const retryBtn = compiled.querySelector('.btn-retry');
    expect(retryBtn).toBeFalsy();
  });

  it('should show close button when showClose is true', () => {
    fixture.componentRef.setInput('showClose', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const closeBtn = compiled.querySelector('.btn-close');
    expect(closeBtn).toBeTruthy();
  });

  it('should hide close button when showClose is false', () => {
    fixture.componentRef.setInput('showClose', false);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const closeBtn = compiled.querySelector('.btn-close');
    expect(closeBtn).toBeFalsy();
  });

  it('should emit retry event when retry button clicked', () => {
    let retryEmitted = false;
    component.retry.subscribe(() => retryEmitted = true);

    fixture.componentRef.setInput('showRetry', true);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const retryBtn = compiled.querySelector('.btn-retry') as HTMLButtonElement;
    retryBtn.click();

    expect(retryEmitted).toBe(true);
  });

  it('should emit close event when close button clicked', () => {
    let closeEmitted = false;
    component.close.subscribe(() => closeEmitted = true);

    fixture.componentRef.setInput('showClose', true);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const closeBtn = compiled.querySelector('.btn-close') as HTMLButtonElement;
    closeBtn.click();

    expect(closeEmitted).toBe(true);
  });
});
