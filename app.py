import streamlit as st
import requests
import json
import base64
import datetime
import pandas as pd
import numpy as np
from fpdf import FPDF
import io
import time

# Configuración
st.set_page_config(page_title="EduScan Pro", layout="wide")

class BatchExamScanner:
    def __init__(self):
        self.n8n_webhook_url = "https://kitsu-test.app.n8n.cloud/webhook-test/upload-exam"
    
    def process_batch(self, files_data, batch_name, exam_type):
        """Envía todo el lote en un solo request"""
        try:
            # Preparar datos del lote
            batch_payload = {
                "batch_name": batch_name,
                "exam_type": exam_type,
                "timestamp": datetime.datetime.now().isoformat(),
                "total_exams": len(files_data),
                "exams": []
            }
            
            # Convertir todas las imágenes a base64
            for file_data in files_data:
                image_bytes = file_data['file'].getvalue()
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                batch_payload["exams"].append({
                    "student_id": file_data['student_id'],
                    "filename": file_data['filename'],
                    "image_data": f"data:image/png;base64,{image_b64}"
                })
            
            headers = {'Content-Type': 'application/json'}
            
            # Un solo request con timeout largo
            response = requests.post(
                self.n8n_webhook_url, 
                json=batch_payload, 
                headers=headers,
                timeout=300  # 5 minutos para procesar todo el lote
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'batch_size': len(files_data)
                }
            else:
                return {
                    'success': False,
                    'error': f"Error HTTP {response.status_code}",
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

class PDFReportGenerator:
    def __init__(self):
        self.colors = {
            'primary': (41, 128, 185),
            'secondary': (52, 152, 219),
            'success': (39, 174, 96),
            'warning': (241, 196, 15),
            'danger': (231, 76, 60),
            'dark': (44, 62, 80),
            'light': (236, 240, 241)
        }
    
    def draw_header(self, pdf, title):
        """Dibuja el encabezado del reporte"""
        pdf.set_fill_color(*self.colors['primary'])
        pdf.rect(0, 0, 210, 30, 'F')
        
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 20)
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)
    
    def draw_footer(self, pdf):
        """Dibuja el pie de página"""
        pdf.set_y(-15)
        pdf.set_font("Arial", 'I', 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 10, f"Página {pdf.page_no()} - Generado con EduScan Pro", 0, 0, 'C')
    
    def create_metric_box(self, pdf, x, y, width, height, title, value, color):
        """Crea una caja de métrica con estilo usando métodos estándar de FPDF"""
        # Dibujar rectángulo de fondo
        pdf.set_fill_color(*color)
        pdf.rect(x, y, width, height, 'F')
        
        # Dibujar borde
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(x, y, width, height)
        
        # Texto del título
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_xy(x + 5, y + 3)
        pdf.cell(width - 10, 5, title, 0, 1)
        
        # Valor
        pdf.set_font("Arial", 'B', 14)
        pdf.set_xy(x + 5, y + 9)
        pdf.cell(width - 10, 8, str(value), 0, 1)
    
    def create_student_metric_box(self, pdf, x, y, width, height, title, student_name, score, color):
        """Crea una caja de métrica especial para estudiantes"""
        # Dibujar rectángulo de fondo
        pdf.set_fill_color(*color)
        pdf.rect(x, y, width, height, 'F')
        
        # Dibujar borde
        pdf.set_draw_color(200, 200, 200)
        pdf.rect(x, y, width, height)
        
        # Texto del título
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_xy(x + 5, y + 3)
        pdf.cell(width - 10, 5, title, 0, 1)
        
        # Puntaje
        pdf.set_font("Arial", 'B', 12)
        pdf.set_xy(x + 5, y + 9)
        pdf.cell(width - 10, 6, f"{score}%", 0, 1)
        
        # Nombre del estudiante
        pdf.set_font("Arial", '', 8)
        pdf.set_xy(x + 5, y + 16)
        # Acortar nombre si es muy largo
        display_name = student_name[:20] + "..." if len(student_name) > 20 else student_name
        pdf.cell(width - 10, 5, display_name, 0, 1)
    
    def generate_pdf_report(self, results_data, batch_name, exam_type):
        """Genera un reporte PDF profesional con los resultados"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Encabezado
        self.draw_header(pdf, "REPORTE DE EVALUACIÓN - EDUSCAN PRO")
        
        # Información del lote - CORREGIDO: Más espacio después del header
        pdf.ln(15)  # Aumenté el espacio aquí
        
        pdf.set_text_color(0, 0, 0)  # Texto negro
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "INFORMACIÓN DEL LOTE", 0, 1)
        
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"Nombre del lote: {batch_name}", 0, 1)
        pdf.cell(0, 6, f"Tipo de examen: {exam_type}", 0, 1)
        pdf.cell(0, 6, f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
        pdf.ln(10)
        
        batch_processing = results_data.get('batch_processing', {})
        results = results_data.get('results', [])
        successful_results = [r for r in results if r.get('success')]
        
        if successful_results:
            # Calcular estadísticas
            scores = []
            approved = 0
            failed = 0
            student_scores = []
            
            for result in successful_results:
                data = result.get('data', {})
                evaluation = data.get('evaluation', {})
                score_percentage = evaluation.get('score_percentage', 0)
                scores.append(score_percentage)
                
                student_name = data.get('student_info', {}).get('student_name', result.get('student_id', 'Desconocido'))
                student_scores.append({
                    'name': student_name,
                    'score': score_percentage,
                    'status': evaluation.get('passing_status', 'REPROBADO')
                })
                
                if evaluation.get('passing_status') == 'APROBADO':
                    approved += 1
                else:
                    failed += 1
            
            # Estadísticas
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            min_score = min(scores) if scores else 0
            
            # Encontrar estudiantes con máxima y mínima nota
            max_students = [s for s in student_scores if s['score'] == max_score]
            min_students = [s for s in student_scores if s['score'] == min_score]
            
            # Métricas principales
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "ESTADÍSTICAS GENERALES", 0, 1)
            pdf.ln(5)
            
            # Crear cuadrícula de métricas mejorada
            metrics_row1 = [
                {"title": "PROMEDIO", "value": f"{avg_score:.1f}%", "color": self.colors['primary']},
                {"title": "APROBADOS", "value": f"{approved}", "color": self.colors['success']},
                {"title": "DESAPROBADOS", "value": f"{failed}", "color": self.colors['danger']}
            ]
            
            # Dibujar primera fila de métricas
            for i, metric in enumerate(metrics_row1):
                x = 10 + i * 63
                y = pdf.get_y()
                self.create_metric_box(pdf, x, y, 60, 20, metric["title"], metric["value"], metric["color"])
            
            pdf.ln(25)
            
            # Segunda fila con información de estudiantes destacados
            current_y = pdf.get_y()
            
            if max_students:
                max_student = max_students[0]
                x_max = 10
                self.create_student_metric_box(
                    pdf, x_max, current_y, 90, 25, 
                    "MEJOR NOTA", 
                    max_student['name'], 
                    max_score, 
                    self.colors['warning']
                )
            
            if min_students:
                min_student = min_students[0]
                x_min = 110
                self.create_student_metric_box(
                    pdf, x_min, current_y, 90, 25, 
                    "NOTA MÁS BAJA", 
                    min_student['name'], 
                    min_score, 
                    self.colors['secondary']
                )
            
            pdf.ln(35)
            
            # Distribución de notas - CORREGIDO: Texto negro en encabezados
            pdf.set_text_color(0, 0, 0)  # ✅ TEXTO NEGRO
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "DISTRIBUCIÓN DE NOTAS", 0, 1)
            pdf.ln(5)
            
            # Crear tabla de distribución CORREGIDA
            header_fill = self.colors['light']
            pdf.set_fill_color(*header_fill)
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO para encabezados
            
            # Encabezado de tabla
            pdf.cell(70, 8, "Rango de Notas", 1, 0, 'C', True)
            pdf.cell(40, 8, "Cantidad", 1, 0, 'C', True)
            pdf.cell(40, 8, "Porcentaje", 1, 1, 'C', True)
            
            ranges = [
                ("90-100% (Excelente)", 90, 100),
                ("80-89% (Muy Bueno)", 80, 89),
                ("70-79% (Bueno)", 70, 79),
                ("60-69% (Suficiente)", 60, 69),
                ("0-59% (Insuficiente)", 0, 59)
            ]
            
            pdf.set_font("Arial", '', 9)
            pdf.set_fill_color(255, 255, 255)  # Fondo blanco para las filas
            pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO para datos
            
            for i, (range_name, min_val, max_val) in enumerate(ranges):
                count = len([s for s in scores if min_val <= s <= max_val])
                percentage = (count / len(scores)) * 100 if scores else 0
                
                # Alternar colores de fondo para mejor legibilidad
                fill = i % 2 == 0
                if fill:
                    pdf.set_fill_color(245, 245, 245)  # Gris muy claro
                else:
                    pdf.set_fill_color(255, 255, 255)  # Blanco
                
                pdf.cell(70, 7, range_name, 1, 0, 'L', fill)
                pdf.cell(40, 7, str(count), 1, 0, 'C', fill)
                pdf.cell(40, 7, f"{percentage:.1f}%", 1, 1, 'C', fill)
            
            pdf.ln(10)
            
            # Ranking de estudiantes - CORREGIDO: Texto negro en encabezados
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "RANKING DE ESTUDIANTES", 0, 1)
            pdf.ln(5)
            
            # Ordenar estudiantes por puntaje
            student_scores.sort(key=lambda x: x['score'], reverse=True)
            
            col_widths = [80, 30, 30, 30]
            
            # Encabezado de tabla - CORREGIDO: Texto negro
            pdf.set_fill_color(*self.colors['light'])
            pdf.set_font("Arial", 'B', 10)
            pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO para encabezados
            
            pdf.cell(col_widths[0], 8, "Estudiante", 1, 0, 'C', True)
            pdf.cell(col_widths[1], 8, "Nota", 1, 0, 'C', True)
            pdf.cell(col_widths[2], 8, "Estado", 1, 0, 'C', True)
            pdf.cell(col_widths[3], 8, "Correctas", 1, 1, 'C', True)
            
            pdf.set_font("Arial", '', 9)
            pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO para datos de estudiantes
            
            for i, student in enumerate(student_scores):
                # Buscar datos completos del estudiante
                student_data = next((r for r in successful_results 
                                  if r.get('data', {}).get('student_info', {}).get('student_name') == student['name']), None)
                
                correct_answers = "N/A"
                if student_data:
                    correct_answers = student_data.get('data', {}).get('evaluation', {}).get('correct_answers', 'N/A')
                
                # Color según estado - PERO texto negro para nombres y datos
                if student['status'] == 'APROBADO':
                    status_color = (39, 174, 96)  # Verde para estado
                else:
                    status_color = (231, 76, 60)  # Rojo para estado
                
                # Fondo alternado para mejor legibilidad
                fill = i % 2 == 0
                if fill:
                    pdf.set_fill_color(245, 245, 245)  # Gris muy claro
                else:
                    pdf.set_fill_color(255, 255, 255)  # Blanco
                
                # Resaltar estudiantes con máxima y mínima nota
                if student['score'] == max_score:
                    pdf.set_fill_color(255, 255, 150)  # Amarillo claro para mejor nota
                elif student['score'] == min_score:
                    pdf.set_fill_color(255, 200, 200)  # Rojo claro para peor nota
                
                # Nombre del estudiante - TEXTO NEGRO
                pdf.set_text_color(0, 0, 0)
                pdf.cell(col_widths[0], 7, student['name'][:25], 1, 0, 'L', True)
                
                # Nota - TEXTO NEGRO
                pdf.cell(col_widths[1], 7, f"{student['score']}%", 1, 0, 'C', True)
                
                # Estado - Color según aprobado/reprobado
                pdf.set_text_color(*status_color)
                pdf.cell(col_widths[2], 7, student['status'], 1, 0, 'C', True)
                
                # Correctas - TEXTO NEGRO
                pdf.set_text_color(0, 0, 0)
                pdf.cell(col_widths[3], 7, str(correct_answers), 1, 1, 'C', True)
            
            pdf.ln(15)
            
            # Resultados detallados por estudiante - CORREGIDO: Texto negro
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "RESULTADOS DETALLADOS POR ESTUDIANTE", 0, 1)
            pdf.ln(5)
            
            for i, result in enumerate(successful_results):
                if i > 0:
                    pdf.add_page()
                    self.draw_header(pdf, "REPORTE DE EVALUACIÓN - EDUSCAN PRO")
                    pdf.ln(10)
                
                data = result.get('data', {})
                student_info = data.get('student_info', {})
                evaluation = data.get('evaluation', {})
                detailed_results = data.get('detailed_results', [])
                
                student_name = student_info.get('student_name', result.get('student_id', 'Desconocido'))
                student_score = evaluation.get('score_percentage', 0)
                
                # Información del estudiante - CORREGIDO: Texto negro
                pdf.set_fill_color(*self.colors['light'])
                pdf.set_font("Arial", 'B', 12)
                pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO
                pdf.cell(0, 8, f"ESTUDIANTE: {student_name}", 1, 1, 'L', True)
                
                pdf.set_font("Arial", '', 10)
                pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO
                pdf.cell(0, 6, f"Tipo de examen: {student_info.get('exam_type', 'N/A')}", 0, 1)
                pdf.cell(0, 6, f"Total de preguntas: {student_info.get('total_questions', 0)}", 0, 1)
                
                # Resumen de evaluación - CORREGIDO: Texto negro en encabezados
                col_width = 47.5
                pdf.ln(5)
                
                # Encabezado de resumen - TEXTO NEGRO
                pdf.set_fill_color(*self.colors['light'])
                pdf.set_font("Arial", 'B', 10)
                pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO para encabezados
                pdf.cell(col_width, 8, "Correctas:", 1, 0, 'C', True)
                pdf.cell(col_width, 8, "Incorrectas:", 1, 0, 'C', True)
                pdf.cell(col_width, 8, "Puntaje:", 1, 0, 'C', True)
                pdf.cell(col_width, 8, "Estado:", 1, 1, 'C', True)
                
                # Datos del resumen - TEXTO NEGRO para valores
                pdf.set_font("Arial", '', 10)
                pdf.set_fill_color(255, 255, 255)  # Fondo blanco
                
                # Correctas - TEXTO NEGRO
                pdf.set_text_color(0, 0, 0)
                pdf.cell(col_width, 8, str(evaluation.get('correct_answers', 0)), 1, 0, 'C', True)
                
                # Incorrectas - TEXTO NEGRO
                pdf.cell(col_width, 8, str(evaluation.get('incorrect_answers', 0)), 1, 0, 'C', True)
                
                # Puntaje - TEXTO NEGRO
                pdf.cell(col_width, 8, f"{student_score}%", 1, 0, 'C', True)
                
                # Estado - Color según aprobado/reprobado
                status_color = (39, 174, 96) if evaluation.get('passing_status') == 'APROBADO' else (231, 76, 60)
                pdf.set_text_color(*status_color)
                pdf.cell(col_width, 8, evaluation.get('passing_status', 'N/A'), 1, 1, 'C', True)
                pdf.set_text_color(0, 0, 0)  # Reset a negro
                
                pdf.ln(8)
                
                # Resultados detallados
                if detailed_results:
                    pdf.set_font("Arial", 'B', 11)
                    pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO
                    pdf.cell(0, 8, "DETALLE DE RESPUESTAS:", 0, 1)
                    pdf.ln(3)
                    
                    # Encabezado de tabla detallada - TEXTO NEGRO
                    header_fill = self.colors['light']
                    pdf.set_fill_color(*header_fill)
                    pdf.set_font("Arial", 'B', 8)
                    pdf.set_text_color(0, 0, 0)  # TEXTO NEGRO para encabezados
                    
                    pdf.cell(15, 8, "Preg.", 1, 0, 'C', True)
                    pdf.cell(20, 8, "Selección", 1, 0, 'C', True)
                    pdf.cell(20, 8, "Correcta", 1, 0, 'C', True)
                    pdf.cell(15, 8, "Estado", 1, 0, 'C', True)
                    pdf.cell(120, 8, "Explicación", 1, 1, 'C', True)
                    
                    pdf.set_font("Arial", '', 7)
                    
                    for j, detail in enumerate(detailed_results):
                        is_correct = detail.get('is_correct', False)
                        
                        # Fondo alternado para mejor legibilidad
                        fill = j % 2 == 0
                        if fill:
                            pdf.set_fill_color(245, 245, 245)  # Gris muy claro
                        else:
                            pdf.set_fill_color(255, 255, 255)  # Blanco
                        
                        # Pregunta - TEXTO NEGRO
                        pdf.set_text_color(0, 0, 0)
                        pdf.cell(15, 6, str(detail.get('question_number', '')), 1, 0, 'C', fill)
                        # Selección - TEXTO NEGRO
                        pdf.cell(20, 6, detail.get('selected_option', 'N/A'), 1, 0, 'C', fill)
                        # Correcta - TEXTO NEGRO
                        pdf.cell(20, 6, detail.get('correct_option', 'N/A'), 1, 0, 'C', fill)
                        
                        # Estado - Color según correcto/incorrecto
                        if is_correct:
                            pdf.set_text_color(39, 174, 96)
                            status = "OK"
                        else:
                            pdf.set_text_color(231, 76, 60)
                            status = "X"
                        pdf.cell(15, 6, status, 1, 0, 'C', fill)
                        
                        # Explicación - TEXTO NEGRO
                        pdf.set_text_color(0, 0, 0)
                        explanation = detail.get('explanation', 'Sin explicación')
                        safe_explanation = self.clean_text(explanation)
                        display_explanation = safe_explanation[:75] + ("..." if len(safe_explanation) > 75 else "")
                        pdf.cell(120, 6, display_explanation, 1, 1, 'L', fill)
                    
                    pdf.ln(10)
        
        # Pie de página en cada página
        self.draw_footer(pdf)
        
        return pdf

    def clean_text(self, text):
        """Limpia el texto de caracteres Unicode problemáticos"""
        if not text:
            return ""
        
        # Reemplazar caracteres Unicode problemáticos
        replacements = {
            '✓': '(OK)',
            '✗': '(X)',
            '✅': '(OK)',
            '❌': '(X)',
            '→': '->',
            '←': '<-',
            '—': '-',
            '–': '-',
            '“': '"',
            '”': '"',
            '‘': "'",
            '’': "'",
            '…': '...'
        }
        
        cleaned_text = text
        for char, replacement in replacements.items():
            cleaned_text = cleaned_text.replace(char, replacement)
        
        return cleaned_text

def main():
    st.title("🎓 EduScan Pro - Evaluación por Lotes")
    
    scanner = BatchExamScanner()
    pdf_generator = PDFReportGenerator()
    
    # Inicializar estado de sesión
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'last_results' not in st.session_state:
        st.session_state.last_results = None
    if 'pdf_generated' not in st.session_state:
        st.session_state.pdf_generated = False
    
    # Sidebar
    with st.sidebar:
        st.header("Configuración del Lote")
        batch_name = st.text_input("Nombre del Lote", placeholder="Grupo A - Matemáticas")
        exam_type = st.selectbox("Tipo de Examen", ["Matemáticas", "Ciencias", "Historia", "Inglés"])
        
        st.markdown("---")
        st.markdown("**💡 Instrucciones:**")
        st.markdown("1. Sube todos los exámenes a la vez")
        st.markdown("2. El sistema procesará todo el lote")
        st.markdown("3. Los resultados llegarán juntos")
    
    # Área principal
    st.subheader("📤 Subida de Exámenes")
    
    uploaded_files = st.file_uploader(
        "Selecciona todos los exámenes del lote",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="Puedes seleccionar múltiples archivos a la vez"
    )
    
    # Mostrar archivos seleccionados
    if uploaded_files:
        st.write(f"📁 **Archivos seleccionados:** {len(uploaded_files)} exámenes")
        for i, file in enumerate(uploaded_files):
            st.write(f"{i+1}. {file.name}")
    
    # Procesar lote completo
    if uploaded_files and batch_name and not st.session_state.processing and not st.session_state.pdf_generated:
        if st.button("🚀 Procesar Lote Completo", type="primary", use_container_width=True):
            if len(uploaded_files) > 10:
                st.warning("⚠️ Tienes muchos exámenes. El procesamiento puede tomar varios minutos.")
            
            st.session_state.processing = True
            
            # Preparar datos
            files_data = []
            for uploaded_file in uploaded_files:
                student_id = uploaded_file.name.split('.')[0]
                files_data.append({
                    'file': uploaded_file,
                    'student_id': student_id,
                    'filename': uploaded_file.name
                })
            
            # Procesar lote
            with st.spinner(f"🔄 Procesando {len(uploaded_files)} exámenes. Esto puede tomar varios minutos..."):
                result = scanner.process_batch(files_data, batch_name, exam_type)
                st.session_state.last_results = result
                st.session_state.processing = False
            
            # Mostrar resultados
            if result['success']:
                st.success(f"✅ Lote procesado exitosamente!")
                
                # Mostrar resumen visual
                results_data = result['data']
                batch_processing = results_data.get('batch_processing', {})
                results = results_data.get('results', [])
                successful_results = [r for r in results if r.get('success')]
                
                if successful_results:
                    # Calcular estadísticas para mostrar en Streamlit
                    scores = []
                    approved = 0
                    student_scores = []
                    
                    for result_item in successful_results:
                        data = result_item.get('data', {})
                        evaluation = data.get('evaluation', {})
                        score = evaluation.get('score_percentage', 0)
                        scores.append(score)
                        
                        student_name = data.get('student_info', {}).get('student_name', result_item.get('student_id', 'Desconocido'))
                        student_scores.append({
                            'name': student_name,
                            'score': score
                        })
                        
                        if evaluation.get('passing_status') == 'APROBADO':
                            approved += 1
                    
                    avg_score = sum(scores) / len(scores) if scores else 0
                    max_score = max(scores) if scores else 0
                    min_score = min(scores) if scores else 0
                    
                    # Encontrar estudiantes con máxima nota
                    max_students = [s for s in student_scores if s['score'] == max_score]
                    
                    # Mostrar métricas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📊 Promedio General", f"{avg_score:.1f}%")
                    with col2:
                        st.metric("✅ Aprobados", approved)
                    with col3:
                        st.metric("❌ Desaprobados", len(successful_results) - approved)
                    with col4:
                        st.metric("🎯 Nota Máxima", f"{max_score}%")
                    
                    # Mostrar información del estudiante con máxima nota
                    if max_students:
                        st.info(f"🏆 **Mejor desempeño:** {max_students[0]['name']} con {max_score}%")
                    
                    # Generar PDF automáticamente
                    st.subheader("📄 Reporte PDF Generado")

                    try:
                        pdf = pdf_generator.generate_pdf_report(results_data, batch_name, exam_type)
                        
                        # Guardar PDF en buffer
                        pdf_buffer = io.BytesIO()
                        pdf_output = pdf.output(dest='S')

                        # ✅ Corregir compatibilidad según el tipo devuelto
                        if isinstance(pdf_output, str):
                            pdf_output = pdf_output.encode('latin-1')
                        elif isinstance(pdf_output, bytearray):
                            pdf_output = bytes(pdf_output)

                        pdf_buffer.write(pdf_output)
                        pdf_buffer.seek(0)
                        
                        # Botón de descarga
                        st.download_button(
                            label="⬇️ Descargar Reporte PDF",
                            data=pdf_buffer,
                            file_name=f"reporte_eduscan_{batch_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        st.session_state.pdf_generated = True
                        
                    except Exception as e:
                        st.error(f"❌ Error al generar PDF: {str(e)}")

                    
                    # Botón para procesar nuevo lote
                    if st.button("🔄 Procesar Nuevo Lote", use_container_width=True):
                        st.session_state.last_results = None
                        st.session_state.processing = False
                        st.session_state.pdf_generated = False
                        st.rerun()
            else:
                st.error(f"❌ Error al procesar lote: {result['error']}")
    
    # Si ya se generó PDF, mostrar opción para nuevo lote
    elif st.session_state.pdf_generated:
        st.info("📄 El reporte PDF ha sido generado. Puedes descargarlo arriba.")
        if st.button("🔄 Procesar Nuevo Lote", use_container_width=True):
            st.session_state.last_results = None
            st.session_state.processing = False
            st.session_state.pdf_generated = False
            st.rerun()

if __name__ == "__main__":
    main()