from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import sys
import os

# Agregar el directorio padre al path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import Config

class SeleniumHandler:
    def __init__(self):
        self.driver = None
        self.config = Config()
    
    def setup_driver(self):
        """Configurar el navegador"""
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        return self.driver
    
    def wait_and_find(self, by, locator, timeout=None, scroll_into_view=False):
        """Esperar y encontrar elemento con scroll opcional"""
        if timeout is None:
            timeout = self.config.WEBDRIVER_TIMEOUT
            
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        
        if scroll_into_view:
            self.driver.execute_script(
                f"arguments[0].scrollIntoView({{behavior: '{self.config.SCROLL_BEHAVIOR}', block: 'center'}});", 
                element
            )
        
        return element
    
    def find_elements_safe(self, by, locator, timeout=1):
        """Buscar elementos de forma segura sin excepciones"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            return self.driver.find_elements(by, locator)
        except Exception:
            return None
    
    def find(self, by, locator, timeout=1):
        """Busca elementos y espera a que sean visibles antes de retornarlos - versión del código Tkinter"""
        try:
            # Esperar hasta que el elemento esté presente en el DOM
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            # Esperar hasta que el elemento sea visible
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            return self.driver.find_elements(by, locator)  # Retorna la lista de elementos visibles
        except Exception as e:
            return None
    
    def login(self, email, password):
        """Función para iniciar sesión en Okta - exacta del código Tkinter"""
        self.driver.get(self.config.LOGIN_URL)
        self.wait_and_find(By.XPATH, "/html/body/div[2]/div[2]/main/div[2]/div/div/div[2]/form/div[1]/div[3]/div[2]/div[2]/span/input").send_keys(email)
        self.wait_and_find(By.XPATH, "/html/body/div[2]/div[2]/main/div[2]/div/div/div[2]/form/div[2]/input").click()
        self.wait_and_find(By.XPATH, "/html/body/div[2]/div[2]/main/div[2]/div/div/div[2]/form/div[1]/div[4]/div/div[2]/span/input").send_keys(password)
        self.wait_and_find(By.XPATH, "/html/body/div[2]/div[2]/main/div[2]/div/div/div[2]/form/div[2]/input").click()
        main_window = self.driver.current_window_handle
        self.wait_and_find(By.XPATH, "/html/body/div[2]/div[2]/main/div[2]/div/div/div[2]/form/div[2]/div/div[2]/div[2]/div[2]").click()
        self.driver.switch_to.window(main_window)
        self.wait_and_find(By.XPATH, "//*[@id='main-content']/section/section/section/div/section/div/a[@aria-label='launch app Replicon']",30).click()
        self.switch_to_replicon()
    
    def switch_to_replicon(self):
        """Función para cambiar a la ventana de Replicon - exacta del código Tkinter"""
        WebDriverWait(self.driver, 30).until(lambda d: len(d.window_handles) > 1)
        all_windows = self.driver.window_handles
        replicon_window = None
        
        for window in all_windows:
            self.driver.switch_to.window(window)
            if "replicon" in self.driver.current_url:
                replicon_window = window
                break
        
        for window in all_windows:
            if window != replicon_window:
                self.driver.switch_to.window(window)
                self.driver.close()
        
        if replicon_window:
            self.driver.switch_to.window(replicon_window)
        else:
            raise Exception("No se encontró la ventana de Replicon.")
    
    def select_month(self):
        """Seleccionar mes actual en Replicon"""
        self.wait_and_find(By.CLASS_NAME, "userWelcomeText")
        self.wait_and_find(
            By.XPATH, 
            "/html/body/div[1]/div[3]/div[3]/div/div[2]/div[1]/overview-page/div[2]/div/div[1]/div[3]/timesheet-card/div/article/current-timesheet-card-item/div//ul/li"
        ).click()
    
    def add_time_entry(self, entry):
        """Agregar entrada de tiempo con estrategias mejoradas"""
        start_time = entry["start_time"]
        end_time = entry["end_time"]
        project = entry["project"]
        account = entry["account"]
        
        try:
            # Configurar hora de inicio - usar múltiples selectores
            time_input = self.wait_and_find_multiple([
                (By.XPATH, "//table[@class='fieldTable fieldTableNarrow']//input[@class='time']"),
                (By.XPATH, "//input[@class='time']"),
                (By.CSS_SELECTOR, "input.time")
            ])
            time_input.clear()
            time_input.send_keys(start_time)
            
            # Seleccionar proyecto - múltiples selectores para el dropdown
            project_dropdown = self.wait_and_find_multiple([
                (By.XPATH, "//table[@class='fieldTable fieldTableNarrow']//a[@class='divDropdown multiLevelSelector divDropdownSelectionNeeded']"),
                (By.XPATH, "//a[@class='divDropdown multiLevelSelector divDropdownSelectionNeeded']"),
                (By.CSS_SELECTOR, "a.divDropdown.multiLevelSelector.divDropdownSelectionNeeded")
            ])
            project_dropdown.click()
            
            # Esperar y seleccionar proyecto específico
            project_link = self.wait_and_find_multiple([
                (By.XPATH, f"//a[contains(text(),'{project}')]"),
                (By.XPATH, f"//li//a[text()='{project}']"),
                (By.XPATH, f"//*[contains(text(),'{project}')]//ancestor::a")
            ])
            project_link.click()
            
            # Seleccionar cuenta/subproyecto
            account_link = self.wait_and_find_multiple([
                (By.XPATH, f"//*[@class='listArea overthrow']//a[contains(text(),'{account}')]"),
                (By.XPATH, f"//a[contains(text(),'{account}')]"),
                (By.XPATH, f"//li//a[text()='{account}']")
            ])
            account_link.click()
            
            # Esperar que se cargue la selección
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "loading"))
            )
            
            # Guardar entrada - múltiples selectores para el botón OK
            save_button = self.wait_and_find_multiple([
                (By.XPATH, "//*[@class='contextPopupNode editPunchDialog']//input[@value='OK']"),
                (By.XPATH, "//input[@value='OK']"),
                (By.XPATH, "//div[contains(@class,'editPunchDialog')]//input[1]")
            ])
            save_button.click()
            
            # Esperar que se guarde la entrada de inicio
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "contextPopupNode"))
            )
            
            # Configurar hora de fin - buscar el botón de salida
            checkout_button = self.wait_and_find_multiple([
                (By.XPATH, "//*[@class='componentPunchSegment combinedInput']//a[2][count(span)=1]"),
                (By.XPATH, "//a[contains(@class,'punchOut')]"),
                (By.XPATH, "//div[contains(@class,'combinedInput')]//a[2]")
            ])
            checkout_button.click()
            
            # Configurar hora de fin
            end_time_input = self.wait_and_find_multiple([
                (By.XPATH, "//table[@class='fieldTable fieldTableNarrow']//input[@class='time']"),
                (By.XPATH, "//input[@class='time']"),
                (By.CSS_SELECTOR, "input.time")
            ])
            end_time_input.clear()
            end_time_input.send_keys(end_time)
            
            # Guardar salida
            save_end_button = self.wait_and_find_multiple([
                (By.XPATH, "//*[@class='contextPopupNode editPunchDialog']//input[@value='OK']"),
                (By.XPATH, "//input[@value='OK']"),
                (By.XPATH, "//div[contains(@class,'editPunchDialog')]//input[1]")
            ])
            save_end_button.click()
            
            # Esperar que se complete la entrada
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "contextPopupNode"))
            )
            
        except Exception as e:
            raise Exception(f"Error al agregar entrada de tiempo: {e}")
    
    def wait_and_find_multiple(self, selectors, timeout=10):
        """Intentar múltiples selectores hasta que uno funcione"""
        for by, locator in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, locator))
                )
                return element
            except:
                continue
        
        # Si ningún selector funciona, lanzar excepción con todos los intentos
        selectors_str = ", ".join([f"{by}='{locator}'" for by, locator in selectors])
        raise Exception(f"No se pudo encontrar elemento con ninguno de estos selectores: {selectors_str}")
    
    def batch_entries_same_day(self, time_entries_data, progress_callback=None):
        """Procesar entradas por día con mejor manejo de errores"""
        total_days = len(time_entries_data)
        
        for day_index, daily_entries in enumerate(time_entries_data):
            try:
                current_day = day_index + 2  # Los días empiezan desde li[2]
                
                # Verificar si es día de vacaciones o feriado
                if self.is_vacation_or_holiday(current_day):
                    if progress_callback:
                        progress_callback(day_index + 1, total_days, f"Saltando día {current_day-1} (vacaciones/feriado)")
                    continue
                
                # Verificar si hay entradas de trabajo para este día
                work_entries = [entry for entry in daily_entries 
                              if entry["project"] not in ["Vacation", "No work", "Weekend", "ND"]]
                
                if not work_entries:
                    if progress_callback:
                        progress_callback(day_index + 1, total_days, f"Saltando día {current_day-1} (sin trabajo)")
                    continue
                
                # Hacer clic en el día
                day_element = self.wait_and_find_multiple([
                    (By.XPATH, f"//li[{current_day}]/ul/li/a"),
                    (By.XPATH, f"//li[{current_day}]//a[contains(@class,'timeEntryCell')]"),
                    (By.XPATH, f"//li[{current_day}]//*[contains(@class,'clickable')]")
                ])
                
                # Scroll al elemento antes de hacer clic
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                    day_element
                )
                day_element.click()
                
                # Procesar cada entrada de trabajo
                for entry_index, entry in enumerate(work_entries):
                    try:
                        if progress_callback:
                            progress_callback(
                                day_index + 1, total_days, 
                                f"Día {current_day-1}: Agregando entrada {entry_index + 1}/{len(work_entries)}"
                            )
                        
                        self.add_time_entry(entry)
                        
                        # Pequeña pausa entre entradas del mismo día
                        WebDriverWait(self.driver, 3).until(
                            lambda d: len(d.find_elements(By.CLASS_NAME, "contextPopupNode")) == 0
                        )
                        
                    except Exception as e:
                        error_msg = f"Error en día {current_day-1}, entrada {entry_index + 1}: {e}"
                        if progress_callback:
                            progress_callback(day_index + 1, total_days, error_msg)
                        raise Exception(error_msg)
                
                if progress_callback:
                    progress_callback(day_index + 1, total_days, f"Día {current_day-1} completado")
                    
            except Exception as e:
                error_msg = f"Error al procesar día {current_day-1}: {e}"
                if progress_callback:
                    progress_callback(day_index + 1, total_days, error_msg)
                raise Exception(error_msg)
    
    def process_all_entries(self, time_entries_data, progress_callback=None):
        """Función para procesar todas las entradas - basada exactamente en start_process del código Tkinter"""
        for i, inner_list in enumerate(time_entries_data, start=2):
            sleep(1)
            if (self.find(By.XPATH, f"//li[{i}]/ul/li/div/span[contains(text(), 'Col-Vacations')]") or 
                self.find(By.XPATH, f"//li[{i}]/div/div[@class='holidayIndicator']")):
                continue
            
            for entry in inner_list:
                if entry["project"] in ["Vacation", "No work"]:
                    continue
                
                sleep(1)
                self.wait_and_find(By.XPATH, f"//li[{i}]/ul/li/a", scroll_into_view=True).click()
                self.add_time_entry(entry)
            sleep(2)
    
    def is_vacation_or_holiday(self, day_number):
        """Verificar si un día es vacación o feriado"""
        try:
            # Buscar indicadores de vacaciones o feriados
            vacation_indicators = [
                (By.XPATH, f"//li[{day_number}]/ul/li/div/span[contains(text(), 'Col-Vacations')]"),
                (By.XPATH, f"//li[{day_number}]/div/div[@class='holidayIndicator']"),
                (By.XPATH, f"//li[{day_number}]//*[contains(@class,'vacation')]"),
                (By.XPATH, f"//li[{day_number}]//*[contains(@class,'holiday')]")
            ]
            
            for by, locator in vacation_indicators:
                try:
                    elements = self.driver.find_elements(by, locator)
                    if elements:
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False