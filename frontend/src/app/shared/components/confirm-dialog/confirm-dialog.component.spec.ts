import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ConfirmDialogComponent, ConfirmDialogData } from './confirm-dialog.component';

describe('ConfirmDialogComponent', () => {
  let component: ConfirmDialogComponent;
  let fixture: ComponentFixture<ConfirmDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConfirmDialogComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ConfirmDialogComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should not be open initially', () => {
    expect(component.isOpen()).toBe(false);
  });

  it('should have default data', () => {
    const data = component.data();
    expect(data.title).toBe('Подтверждение');
    expect(data.message).toBe('Вы уверены?');
    expect(data.type).toBe('info');
  });

  it('should open dialog with data', () => {
    const dialogData: ConfirmDialogData = {
      title: 'Удаление',
      message: 'Вы действительно хотите удалить?',
      type: 'danger'
    };

    component.open(dialogData);
    fixture.detectChanges();

    expect(component.isOpen()).toBe(true);
    expect(component.data().title).toBe('Удаление');
    expect(component.data().message).toBe('Вы действительно хотите удалить?');
    expect(component.data().type).toBe('danger');
  });

  it('should set default texts when not provided', () => {
    const dialogData: ConfirmDialogData = {
      title: 'Test',
      message: 'Test message'
    };

    component.open(dialogData);

    expect(component.data().confirmText).toBe('Подтвердить');
    expect(component.data().cancelText).toBe('Отмена');
    expect(component.data().type).toBe('info');
  });

  it('should use custom button texts', () => {
    const dialogData: ConfirmDialogData = {
      title: 'Test',
      message: 'Test message',
      confirmText: 'Да, удалить',
      cancelText: 'Нет, отменить'
    };

    component.open(dialogData);

    expect(component.data().confirmText).toBe('Да, удалить');
    expect(component.data().cancelText).toBe('Нет, отменить');
  });

  it('should display dialog when open', () => {
    const dialogData: ConfirmDialogData = {
      title: 'Test Title',
      message: 'Test Message'
    };

    component.open(dialogData);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.dialog-overlay')).toBeTruthy();
    expect(compiled.querySelector('.dialog-container')).toBeTruthy();
  });

  it('should display title and message', () => {
    const dialogData: ConfirmDialogData = {
      title: 'Test Title',
      message: 'Test Message'
    };

    component.open(dialogData);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h3')?.textContent).toContain('Test Title');
    expect(compiled.querySelector('.dialog-body p')?.textContent).toContain('Test Message');
  });

  it('should call onConfirm callback when confirm button clicked', () => {
    let confirmed = false;
    const onConfirm = () => { confirmed = true; };

    component.open({
      title: 'Test',
      message: 'Test'
    }, onConfirm);
    fixture.detectChanges();

    const confirmBtn = fixture.nativeElement.querySelector('.btn-confirm') as HTMLButtonElement;
    confirmBtn.click();

    expect(confirmed).toBe(true);
    expect(component.isOpen()).toBe(false);
  });

  it('should call onCancel callback when cancel button clicked', () => {
    let cancelled = false;
    const onCancel = () => { cancelled = true; };

    component.open({
      title: 'Test',
      message: 'Test'
    }, undefined, onCancel);
    fixture.detectChanges();

    const cancelBtn = fixture.nativeElement.querySelector('.btn-cancel') as HTMLButtonElement;
    cancelBtn.click();

    expect(cancelled).toBe(true);
    expect(component.isOpen()).toBe(false);
  });

  it('should call onCancel callback when close X button clicked', () => {
    let cancelled = false;
    const onCancel = () => { cancelled = true; };

    component.open({
      title: 'Test',
      message: 'Test'
    }, undefined, onCancel);
    fixture.detectChanges();

    const closeBtn = fixture.nativeElement.querySelector('.btn-close-x') as HTMLButtonElement;
    closeBtn.click();

    expect(cancelled).toBe(true);
    expect(component.isOpen()).toBe(false);
  });

  it('should call onCancel callback when overlay clicked', () => {
    let cancelled = false;
    const onCancel = () => { cancelled = true; };

    component.open({
      title: 'Test',
      message: 'Test'
    }, undefined, onCancel);
    fixture.detectChanges();

    const overlay = fixture.nativeElement.querySelector('.dialog-overlay') as HTMLElement;
    overlay.click();

    expect(cancelled).toBe(true);
    expect(component.isOpen()).toBe(false);
  });

  it('should apply danger type class', () => {
    component.open({
      title: 'Test',
      message: 'Test',
      type: 'danger'
    });
    fixture.detectChanges();

    const container = fixture.nativeElement.querySelector('.dialog-container');
    expect(container?.classList.contains('dialog-danger')).toBe(true);
  });

  it('should apply warning type class', () => {
    component.open({
      title: 'Test',
      message: 'Test',
      type: 'warning'
    });
    fixture.detectChanges();

    const container = fixture.nativeElement.querySelector('.dialog-container');
    expect(container?.classList.contains('dialog-warning')).toBe(true);
  });

  it('should apply danger button class for danger type', () => {
    component.open({
      title: 'Test',
      message: 'Test',
      type: 'danger'
    });
    fixture.detectChanges();

    const confirmBtn = fixture.nativeElement.querySelector('.btn-confirm');
    expect(confirmBtn?.classList.contains('btn-danger')).toBe(true);
  });

  it('should apply warning button class for warning type', () => {
    component.open({
      title: 'Test',
      message: 'Test',
      type: 'warning'
    });
    fixture.detectChanges();

    const confirmBtn = fixture.nativeElement.querySelector('.btn-confirm');
    expect(confirmBtn?.classList.contains('btn-warning')).toBe(true);
  });

  it('should close without callbacks if none provided', () => {
    component.open({
      title: 'Test',
      message: 'Test'
    });
    fixture.detectChanges();

    expect(component.isOpen()).toBe(true);

    component.onConfirm();
    expect(component.isOpen()).toBe(false);
  });

  it('should not throw error when closing without callbacks', () => {
    component.open({
      title: 'Test',
      message: 'Test'
    });

    expect(() => component.onCancel()).not.toThrow();
    expect(() => component.onConfirm()).not.toThrow();
  });
});
