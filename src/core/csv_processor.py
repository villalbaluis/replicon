import csv
import pandas as pd
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

class CSVProcessor:
    def __init__(self):
        self.csv_filepath = None
        self.chunk_size = 1000  # Procesar en chunks de 1000 filas
        self.max_workers = min(4, multiprocessing.cpu_count())  # Máximo 4 threads
    
    def military_to_standard_time(self, military_time):
        """Convertir hora militar (1600) a formato estándar (4:00pm)"""
        try:
            hour = int(military_time[:2])
            minute = int(military_time[2:])
            
            if hour == 0:
                return f"12:{minute:02d}am"
            elif hour < 12:
                return f"{hour}:{minute:02d}am"
            elif hour == 12:
                return f"12:{minute:02d}pm"
            else:
                return f"{hour-12}:{minute:02d}pm"
        except:
            return military_time  # Retornar original si hay error
    
    def parse_ext_entries(self, ext_string, mapeo_cuentas):
        """Parsear entradas EXT del formato: PROD:PI:1600:1800;PROD:PI:1600:1800"""
        entries = []
        
        if not ext_string.startswith('EXT/'):
            return entries
            
        # Remover 'EXT/' del inicio
        ext_data = ext_string[4:]
        
        # Dividir por ';' para múltiples entradas
        entry_parts = ext_data.split(';')
        
        for part in entry_parts:
            part = part.strip()
            if ':' in part:
                # Formato: PROD:PI:1600:1800
                components = part.split(':')
                if len(components) >= 4:
                    cuenta = components[0].strip()
                    proyecto = components[1].strip()
                    start_military = components[2].strip()
                    end_military = components[3].strip()
                    
                    # Convertir a formato estándar
                    start_time = self.military_to_standard_time(start_military)
                    end_time = self.military_to_standard_time(end_military)
                    
                    # Buscar en mapeo de cuentas
                    company = mapeo_cuentas.get(cuenta, {})
                    project_name = company.get("name", cuenta)  # Usar cuenta original si no se encuentra
                    account_name = company.get("projects", {}).get(proyecto, proyecto)  # Usar proyecto original si no se encuentra
                    
                    entries.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "project": project_name,
                        "account": account_name
                    })
        
        return entries
    
    def set_csv_file(self, filepath):
        """Establecer archivo CSV a procesar"""
        self.csv_filepath = filepath
    
    def process_csv(self, horarios, mapeo_cuentas):
        """Procesar CSV y generar entradas de tiempo"""
        if not self.csv_filepath:
            raise ValueError("No se ha establecido un archivo CSV")
        
        try:
            with open(self.csv_filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Saltar encabezado
                
                time_entries = []
                for row in reader:
                    cuenta, proyecto = row
                    cuenta = cuenta.strip()
                    proyecto = proyecto.strip()
                    
                    company = mapeo_cuentas.get(cuenta, {})
                    project_name = company.get("name", "Desconocido")
                    
                    # Si es día de descanso, crear lista vacía
                    if project_name in ["Vacation", "No work"]:
                        daily_entries = []
                    else:
                        # Solo buscar account_name si NO es día de descanso
                        account_name = company.get("projects", {}).get(proyecto, "Desconocido")
                        
                        # Crear entradas diarias con los horarios configurados
                        daily_entries = [
                            {**h, "project": project_name, "account": account_name} 
                            for h in horarios
                        ]
                    time_entries.append(daily_entries)
                
                return time_entries
                
        except Exception as e:
            raise Exception(f"Error al procesar CSV: {e}")
    
    def process_csv_with_pandas(self, horarios, mapeo_cuentas, progress_callback=None):
        """Procesar CSV usando pandas para mejor rendimiento con chunks y threading"""
        if not self.csv_filepath:
            raise ValueError("No se ha establecido un archivo CSV")
        
        try:
            # Leer CSV en chunks para memoria eficiente
            chunk_reader = pd.read_csv(self.csv_filepath, chunksize=self.chunk_size)
            all_time_entries = []
            total_chunks = 0
            processed_chunks = 0
            
            # Contar chunks para progreso
            with open(self.csv_filepath, 'r') as f:
                total_lines = sum(1 for line in f) - 1  # -1 por header
                total_chunks = (total_lines // self.chunk_size) + 1
            
            if progress_callback:
                progress_callback(f"Procesando {total_lines} filas en {total_chunks} chunks...")
            
            # Procesar chunks en paralelo
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                for chunk in chunk_reader:
                    future = executor.submit(self._process_chunk, chunk, horarios, mapeo_cuentas)
                    futures.append(future)
                
                # Recopilar resultados
                for future in futures:
                    chunk_entries = future.result()
                    all_time_entries.extend(chunk_entries)
                    processed_chunks += 1
                    
                    if progress_callback:
                        progress = (processed_chunks / total_chunks) * 100
                        progress_callback(f"Procesando chunks: {processed_chunks}/{total_chunks} ({progress:.1f}%)")
            
            if progress_callback:
                progress_callback(f"Procesamiento completado: {len(all_time_entries)} días procesados")
            
            return all_time_entries
            
        except Exception as e:
            raise Exception(f"Error al procesar CSV con pandas: {e}")
    
    def _process_chunk(self, chunk, horarios, mapeo_cuentas):
        """Procesar un chunk del CSV"""
        # Limpiar datos
        chunk['Cuenta'] = chunk['Cuenta'].str.strip()
        chunk['Projecto'] = chunk['Projecto'].str.strip()
        
        chunk_entries = []
        
        for _, row in chunk.iterrows():
            cuenta = row['Cuenta']
            proyecto = row['Projecto']
            
            # Verificar si hay columna EXT
            ext_data = None
            if len(row) > 2 and pd.notna(row.iloc[2]):
                ext_data = str(row.iloc[2]).strip()
            
            daily_entries = []
            
            # Si cuenta y proyecto son "ND", solo procesar entradas EXT
            if cuenta.upper() == 'ND' and proyecto.upper() == 'ND':
                # No crear entradas normales, solo procesar EXT
                if ext_data and ext_data.startswith('EXT/'):
                    ext_entries = self.parse_ext_entries(ext_data, mapeo_cuentas)
                    daily_entries.extend(ext_entries)
            else:
                # Procesar entradas normales (usando cache para mapeo)
                company = mapeo_cuentas.get(cuenta, {})
                project_name = company.get("name", "Desconocido")
                
                # Si es día de descanso, no crear entradas
                if project_name in ["Vacation", "No work","Desconocido"]:
                    daily_entries = []
                else:
                    account_name = company.get("projects", {}).get(proyecto, "Desconocido")
                    
                    # Crear entradas diarias normales
                    daily_entries = [
                        {**h, "project": project_name, "account": account_name} 
                        for h in horarios
                    ]
                    
                    # Agregar entradas EXT si existen
                    if ext_data and ext_data.startswith('EXT/'):
                        ext_entries = self.parse_ext_entries(ext_data, mapeo_cuentas)
                        daily_entries.extend(ext_entries)
            
            chunk_entries.append(daily_entries)
        
        return chunk_entries
    
    def calculate_hours_summary(self, time_entries):
        """Calcular resumen de horas trabajadas incluyendo horas semanales y extras"""
        from datetime import datetime, timedelta
        import calendar
        
        total_hours = 0
        total_work_days = 0  # Solo días con trabajo real
        hours_by_project = {}
        hours_by_week = {}
        hours_by_day = []
        
        # Obtener fecha actual para cálculos
        current_date = datetime.now()
        month = current_date.month
        year = current_date.year
    
        
        for day_index, daily_entries in enumerate(time_entries):
            daily_hours = 0
            daily_work_hours = 0  # Solo horas de trabajo, sin vacaciones
            # Solo procesar días válidos del mes
            if day_index + 1 <= calendar.monthrange(year, month)[1]:
                day_date = datetime(year, month, day_index + 1)
                
                for entry in daily_entries:
                    # Calcular horas para esta entrada
                    hours = self._calculate_entry_hours(entry)
                    project = entry.get('project', 'Desconocido')
                    
                    # Agrupar por proyecto (todos los proyectos)
                    if project not in hours_by_project:
                        hours_by_project[project] = 0
                    hours_by_project[project] += hours
                    
                    daily_hours += hours
                    
                    # Solo contar como horas trabajadas si no es vacación o no trabajo
                    if project not in ['Vacation', 'No work', 'Holiday', 'Weekend', 'ND', 'Desconocido']:
                        daily_work_hours += hours
                        total_hours += hours
                
                hours_by_day.append(daily_work_hours)  # Solo horas trabajadas
                
                # Contar día trabajado si tiene horas de trabajo
                if daily_work_hours > 0:
                    total_work_days += 1
                
                # Calcular semana solo para días con trabajo real
                if daily_work_hours > 0:
                    week_number = day_date.isocalendar()[1]
                    week_start = day_date - timedelta(days=day_date.weekday())
                    week_end = week_start + timedelta(days=6)
                    week_key = f"Semana {week_number} ({week_start.strftime('%d/%m')}-{week_end.strftime('%d/%m')})"
                    
                    if week_key not in hours_by_week:
                        hours_by_week[week_key] = {'hours': 0, 'days': 0}
                    
                    hours_by_week[week_key]['hours'] += daily_work_hours
                    hours_by_week[week_key]['days'] += 1
        
        # Calcular horas extra (asumiendo 8 horas estándar por día y 40 por semana)
        standard_hours_per_day = 8
        standard_hours_per_week = 40
        
        # Horas extra diarias
        overtime_daily = sum(max(0, day_hours - standard_hours_per_day) for day_hours in hours_by_day)
        
        # Horas extra semanales - corregido para usar la estructura correcta
        overtime_weekly = sum(max(0, week_data['hours'] - standard_hours_per_week) for week_data in hours_by_week.values())
        
        # Total de horas normales vs extra
        regular_hours = total_hours - overtime_daily
        
        return {
            'total_hours': total_hours,
            'total_days': total_work_days,
            'average_hours_per_day': total_hours / total_work_days if total_work_days > 0 else 0,
            'hours_by_project': hours_by_project,
            'hours_by_week': hours_by_week,
            'hours_by_day': hours_by_day,
            'regular_hours': max(0, regular_hours),
            'overtime_daily': overtime_daily,
            'overtime_weekly': overtime_weekly,
            'standard_hours_per_day': standard_hours_per_day,
            'standard_hours_per_week': standard_hours_per_week
        }
    
    def _calculate_entry_hours(self, entry):
        """Calcular horas de una entrada específica"""
        try:
            start_time = entry.get('start_time', '')
            end_time = entry.get('end_time', '')
            
            # Convertir formato de hora (ej: "7:00am" -> datetime)
            fmt = "%I:%M%p"
            start = datetime.strptime(start_time, fmt)
            end = datetime.strptime(end_time, fmt)
            
            # Calcular diferencia en horas
            diff = end - start
            hours = diff.seconds / 3600
            
            return hours
            
        except Exception:
            return 0  # Retornar 0 si hay error en el formato
    
    def validate_csv_format(self):
        """Validar que el archivo CSV tenga el formato correcto"""
        if not self.csv_filepath:
            return False, "No se ha establecido un archivo CSV"
        
        try:
            df = pd.read_csv(self.csv_filepath)
            
            # Verificar columnas mínimas requeridas
            if len(df.columns) < 2:
                return False, "El CSV debe tener al menos 2 columnas (Cuenta, Projecto)"
            
            # Renombrar columnas para consistencia
            df.columns = ['Cuenta', 'Projecto'] + [f'Extra_{i}' for i in range(len(df.columns)-2)]
            
            # Verificar que no esté vacío
            if df.empty:
                return False, "El archivo CSV está vacío"
            
            # Validar formato de entradas EXT si existen
            validation_errors = []
            for index, row in df.iterrows():
                if len(row) > 2 and pd.notna(row.iloc[2]):
                    ext_data = str(row.iloc[2]).strip()
                    if ext_data and not self._validate_ext_format(ext_data):
                        validation_errors.append(f"Fila {index+2}: Formato EXT inválido: {ext_data}")
            
            if validation_errors:
                return False, "\n".join(validation_errors)
            
            return True, "Formato válido (soporta entradas EXT)"
            
        except Exception as e:
            return False, f"Error al validar CSV: {e}"
    
    def _validate_ext_format(self, ext_string):
        """Validar formato de entrada EXT"""
        if not ext_string.startswith('EXT/'):
            return False
        
        # Remover 'EXT/' y dividir por ';'
        ext_data = ext_string[4:]
        entries = ext_data.split(';')
        
        for entry in entries:
            entry = entry.strip()
            if ':' in entry:
                parts = entry.split(':')
                if len(parts) >= 4:
                    # Validar que las horas sean números de 4 dígitos
                    start_time = parts[2].strip()
                    end_time = parts[3].strip()
                    
                    if not (start_time.isdigit() and len(start_time) == 4):
                        return False
                    if not (end_time.isdigit() and len(end_time) == 4):
                        return False
                    
                    # Validar rango de horas (0000-2359)
                    start_hour = int(start_time[:2])
                    start_min = int(start_time[2:])
                    end_hour = int(end_time[:2])
                    end_min = int(end_time[2:])
                    
                    if not (0 <= start_hour <= 23 and 0 <= start_min <= 59):
                        return False
                    if not (0 <= end_hour <= 23 and 0 <= end_min <= 59):
                        return False
                else:
                    return False
            else:
                return False
        
        return True