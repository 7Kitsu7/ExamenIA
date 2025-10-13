import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import datetime
import time
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="EduScan Pro - Evaluador Inteligente",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Mejorado - Compatible con Modo Oscuro
st.markdown("""
<style>
    /* Estilos generales compatibles con modo oscuro */
    .main > div {
        padding: 2rem 1rem;
    }
    
    /* Títulos y headers - VISIBLES EN MODO OSCURO */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-color) !important;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 3px solid var(--border-color);
        padding-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Variables CSS para modo claro/oscuro */
    :root {
        --text-color: #2d3748;
        --border-color: #e2e8f0;
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --card-bg: white;
        --metric-bg: white;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --text-color: #f7fafc;
            --border-color: #4a5568;
            --primary-color: #7f9cf5;
            --secondary-color: #9f7aea;
            --card-bg: #2d3748;
            --metric-bg: #4a5568;
        }
    }
    
    /* Botones mejorados */
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Tarjeta de puntaje premium */
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: none;
    }
    
    .score-percentage {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .score-details {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        margin-top: 1.5rem;
    }
    
    .score-item {
        flex: 1;
        min-width: 120px;
        margin: 0.5rem;
    }
    
    .score-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .score-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Estilos para métricas de información del examen - COMPATIBLES CON MODO OSCURO */
    .exam-info-container {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .info-metric {
        background: var(--metric-bg);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .info-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-color);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        color: var(--text-color);
    }
    
    /* Tarjetas de preguntas mejoradas */
    .question-card {
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .question-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .correct-answer {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border-left: 5px solid #2f855a;
    }
    
    .incorrect-answer {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
        color: white;
        border-left: 5px solid #c53030;
    }
    
    .unanswered-answer {
        background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
        color: white;
        border-left: 5px solid #4a5568;
    }
    
    .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .question-number {
        font-size: 1.2rem;
        font-weight: 700;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
    }
    
    .question-status {
        font-size: 1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .question-details {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .question-explanation {
        font-style: italic;
        margin-top: 1rem;
        opacity: 0.9;
        border-top: 1px solid rgba(255,255,255,0.3);
        padding-top: 1rem;
    }
    
    /* Sidebar mejorado */
    .sidebar .sidebar-content {
        background: var(--card-bg);
    }
    
    /* Badges para estados */
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-approved {
        background: #48bb78;
        color: white;
    }
    
    .status-failed {
        background: #f56565;
        color: white;
    }
    
    /* Animaciones */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Grade badge mejorado */
    .grade-badge {
        text-align: center;
        padding: 1rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Estilos para exportación */
    .export-section {
        background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px dashed #48bb78;
        margin: 1rem 0;
    }
    
    /* Asegurar que los textos del sidebar sean visibles */
    .sidebar .stTextInput label,
    .sidebar .stSelectbox label,
    .sidebar h2,
    .sidebar h4 {
        color: var(--text-color) !important;
    }
    
    /* Mejorar contraste en modo oscuro */
    .stAlert {
        background-color: var(--card-bg) !important;
    }
</style>
""", unsafe_allow_html=True)

class ExamScanner:
    def __init__(self):
        self.n8n_webhook_url = "https://kitsu-test.app.n8n.cloud/webhook-test/upload-exam"
    
    def process_image(self, image_file, student_id, exam_type):
        """Envía la imagen a n8n para procesamiento"""
        try:
            # Convertir imagen a base64
            image_bytes = image_file.getvalue()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Preparar datos para n8n
            payload = {
                "image_data": f"data:image/png;base64,{image_b64}",
                "student_id": student_id,
                "exam_type": exam_type,
                "upload_timestamp": datetime.datetime.now().isoformat()
            }
            
            # Enviar a n8n con timeout más largo
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.n8n_webhook_url, 
                json=payload, 
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error en el servidor: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            st.error("⏰ El procesamiento está tomando más tiempo de lo esperado. Intenta nuevamente.")
            return None
        except Exception as e:
            st.error(f"Error al procesar la imagen: {str(e)}")
            return None

def get_grade_color(grade):
    """Devuelve el color según la calificación"""
    grade_colors = {
        'A': '#48bb78', 'B': '#68d391', 'C': '#ecc94b', 
        'D': '#ed8936', 'F': '#f56565', 'N/A': '#a0aec0'
    }
    return grade_colors.get(grade, '#a0aec0')

def translate_question_type(question_type):
    """Traduce el tipo de pregunta al español"""
    translations = {
        'multiple_choice': 'Opción Múltiple',
        'true_false': 'Verdadero/Falso',
        'single_choice': 'Selección Simple',
        'multiple_choice_single': 'Opción Múltiple (Una respuesta)',
        'multiple_choice_multiple': 'Opción Múltiple (Múltiples respuestas)'
    }
    return translations.get(question_type, question_type.replace('_', ' ').title())

def create_excel_export(evaluation_data):
    """Crea archivo Excel para exportación"""
    if not evaluation_data:
        return None
    
    evaluation = evaluation_data.get('evaluation', {})
    student_info = evaluation_data.get('student_info', {})
    detailed_results = evaluation_data.get('detailed_results', [])
    
    # Crear buffer para Excel
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        # Hoja 1: Resumen del Examen
        summary_data = {
            'Campo': [
                'ID Estudiante',
                'Tipo de Examen', 
                'Total Preguntas',
                'Preguntas Correctas',
                'Preguntas Incorrectas',
                'Sin Respuesta',
                'Porcentaje de Acierto',
                'Calificación',
                'Estado',
                'Fecha de Procesamiento'
            ],
            'Valor': [
                student_info.get('student_id', 'N/A'),
                student_info.get('exam_type', 'N/A'),
                student_info.get('total_questions', 0),
                evaluation.get('correct_answers', 0),
                evaluation.get('incorrect_answers', 0),
                evaluation.get('unanswered_questions', 0),
                f"{evaluation.get('score_percentage', 0)}%",
                evaluation.get('grade', 'N/A'),
                evaluation.get('passing_status', 'N/A'),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Hoja 2: Preguntas Detalladas
        if detailed_results:
            questions_data = []
            for q in detailed_results:
                questions_data.append({
                    'Número de Pregunta': q.get('question_number'),
                    'Respuesta Seleccionada': q.get('selected_option', 'Sin respuesta'),
                    'Respuesta Correcta': q.get('correct_option', 'N/A'),
                    '¿Es Correcta?': 'Sí' if q.get('is_correct') else 'No',
                    'Tipo de Pregunta': translate_question_type(q.get('question_type', '')),
                    'Explicación': q.get('explanation', '')
                })
            
            questions_df = pd.DataFrame(questions_data)
            questions_df.to_excel(writer, sheet_name='Preguntas Detalladas', index=False)
        
        # Hoja 3: Estadísticas
        stats_data = {
            'Métrica': [
                'Porcentaje de Acierto',
                'Eficiencia',
                'Tasa de Error', 
                'Tasa de Omisión',
                'Nivel de Dificultad'
            ],
            'Valor': [
                f"{evaluation.get('score_percentage', 0)}%",
                f"{(evaluation.get('correct_answers', 0) / student_info.get('total_questions', 1)) * 100:.1f}%",
                f"{(evaluation.get('incorrect_answers', 0) / student_info.get('total_questions', 1)) * 100:.1f}%",
                f"{(evaluation.get('unanswered_questions', 0) / student_info.get('total_questions', 1)) * 100:.1f}%",
                evaluation.get('grade', 'N/A')
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
        
        # Formatear el Excel
        workbook = writer.book
        
        # Formato para el resumen
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })
        
        # Aplicar formato a los headers
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:B' if sheet_name == 'Resumen' else 'A:F', 20)
            for col_num, value in enumerate(stats_df.columns if sheet_name == 'Estadísticas' else summary_df.columns):
                worksheet.write(0, col_num, value, header_format)

    
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def display_results(result_data):
    """Muestra los resultados con diseño mejorado"""
    
    evaluation_data = extract_gemini_response(result_data)
    
    if evaluation_data and not evaluation_data.get('evaluation', {}).get('error'):
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        
        evaluation = evaluation_data.get('evaluation', {})
        student_info = evaluation_data.get('student_info', {})
        detailed_results = evaluation_data.get('detailed_results', [])
        
        # Header de éxito
        col_success, col_grade = st.columns([3, 1])
        with col_success:
            st.success("🎉 ¡Examen evaluado exitosamente!")
        with col_grade:
            grade = evaluation.get('grade', 'N/A')
            grade_color = get_grade_color(grade)
            st.markdown(f"""
            <div class="grade-badge" style="background: {grade_color};">
                <h3 style="margin: 0; font-size: 1.2rem;">Calificación</h3>
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: bold;">{grade}</h1>
            </div>
            """, unsafe_allow_html=True)
        
        # Tarjeta de puntaje mejorada
        st.markdown(f"""
        <div class="score-card fade-in">
            <h1 class="score-percentage">{evaluation.get('score_percentage', 0)}%</h1>
            <div class="score-details">
                <div class="score-item">
                    <h2 class="score-value">{evaluation.get('correct_answers', 0)}</h2>
                    <p class="score-label">✅ Correctas</p>
                </div>
                <div class="score-item">
                    <h2 class="score-value">{evaluation.get('incorrect_answers', 0)}</h2>
                    <p class="score-label">❌ Incorrectas</p>
                </div>
                <div class="score-item">
                    <h2 class="score-value">{evaluation.get('unanswered_questions', 0)}</h2>
                    <p class="score-label">⏭️ Sin respuesta</p>
                </div>
                <div class="score-item">
                    <h2 class="score-value">{student_info.get('total_questions', 0)}</h2>
                    <p class="score-label">📊 Total</p>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <span class="status-badge {'status-approved' if evaluation.get('passing_status') == 'APROBADO' else 'status-failed'}">
                    {evaluation.get('passing_status', 'N/A')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Información del examen
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            📋 Información del Examen
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="exam-info-container fade-in">', unsafe_allow_html=True)
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        
        with info_col1:
            st.markdown(f"""
            <div class="info-metric">
                <div class="metric-icon">👤</div>
                <div class="metric-value">{student_info.get('student_id', 'N/A')}</div>
                <div class="metric-label">ID Estudiante</div>
            </div>
            """, unsafe_allow_html=True)
            
        with info_col2:
            st.markdown(f"""
            <div class="info-metric">
                <div class="metric-icon">📚</div>
                <div class="metric-value">{student_info.get('exam_type', 'N/A')}</div>
                <div class="metric-label">Tipo de Examen</div>
            </div>
            """, unsafe_allow_html=True)
            
        with info_col3:
            st.markdown(f"""
            <div class="info-metric">
                <div class="metric-icon">🔢</div>
                <div class="metric-value">{student_info.get('total_questions', 0)}</div>
                <div class="metric-label">Total Preguntas</div>
            </div>
            """, unsafe_allow_html=True)
            
        with info_col4:
            st.markdown(f"""
            <div class="info-metric">
                <div class="metric-icon">🕐</div>
                <div class="metric-value">Ahora</div>
                <div class="metric-label">Procesado</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Análisis detallado
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            📊 Análisis Detallado por Pregunta
        </div>
        """, unsafe_allow_html=True)
        
        if detailed_results:
            for question in detailed_results:
                question_num = question.get('question_number')
                selected = question.get('selected_option', 'Sin respuesta')
                correct = question.get('correct_option', 'N/A')
                is_correct = question.get('is_correct', False)
                explanation = question.get('explanation', '')
                question_type = translate_question_type(question.get('question_type', 'multiple_choice'))
                
                # Determinar clase y icono
                if selected == 'sin respuesta' or not selected:
                    css_class = "unanswered-answer"
                    icon = "⏭️"
                    status = "SIN RESPUESTA"
                elif is_correct:
                    css_class = "correct-answer"
                    icon = "✅"
                    status = "CORRECTA"
                else:
                    css_class = "incorrect-answer"
                    icon = "❌"
                    status = "INCORRECTA"
                
                st.markdown(f"""
                <div class="question-card {css_class} fade-in">
                    <div class="question-header">
                        <div class="question-number">Pregunta {question_num}</div>
                        <div class="question-status">
                            {icon} {status}
                        </div>
                    </div>
                    <div class="question-details">
                        <div><strong>Tu respuesta:</strong> {selected}</div>
                        <div><strong>Respuesta correcta:</strong> {correct}</div>
                        <div><strong>Tipo:</strong> {question_type}</div>
                    </div>
                    <div class="question-explanation">
                        {explanation}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No se encontraron resultados detallados del análisis.")
        
        # Sección de exportación
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            💾 Exportar Resultados
        </div>
        """, unsafe_allow_html=True)
        
        display_export_section(evaluation_data)
        
        st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        error_msg = evaluation_data.get('evaluation', {}).get('error') if evaluation_data else "No se pudieron extraer los resultados"
        st.error(f"❌ Error en el procesamiento: {error_msg}")
        
        with st.expander("🔍 Ver datos técnicos para debug"):
            st.json(result_data)

def display_export_section(evaluation_data):
    """Muestra la sección de exportación de resultados"""
    st.markdown('<div class="export-section">', unsafe_allow_html=True)
    
    excel_data = create_excel_export(evaluation_data)
    
    if excel_data:
        # Botón único de descarga Excel
        st.download_button(
            label="📊 Descargar Reporte Excel",
            data=excel_data,
            file_name=f"resultado_examen_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Descarga un reporte completo en Excel con resumen, preguntas detalladas y estadísticas"
        )
        
        st.info("""
        **El reporte incluye:**
        - 📋 Resumen completo del examen
        - 📊 Preguntas detalladas con explicaciones  
        - 📈 Estadísticas y métricas de desempeño
        - 🎨 Formato profesional listo para imprimir
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def extract_gemini_response(result_data):
    """Extrae el JSON de la respuesta de Gemini"""
    try:
        # Verificar si ya viene formateado correctamente
        if 'evaluation' in result_data and result_data['evaluation']:
            return result_data
        
        # Buscar en raw_analysis
        if 'raw_analysis' in result_data and 'candidates' in result_data['raw_analysis']:
            candidates = result_data['raw_analysis'].get('candidates', [])
            if candidates and 'content' in candidates[0]:
                parts = candidates[0]['content'].get('parts', [])
                if parts and 'text' in parts[0]:
                    raw_text = parts[0]['text']
                    
                    # Limpiar y parsear
                    clean_text = raw_text.replace('```json', '').replace('```', '').strip()
                    evaluation_data = json.loads(clean_text)
                    return evaluation_data
        
        return None
        
    except Exception as e:
        st.error(f"Error al extraer datos: {str(e)}")
        return None

def main():
    # Header principal
    st.markdown('<h1 class="main-header">🎓 EduScan Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #718096; margin-bottom: 2rem;">Sistema Inteligente de Evaluación Automática</p>', unsafe_allow_html=True)
    
    scanner = ExamScanner()
    
    # Inicializar estado de sesión
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'result_data' not in st.session_state:
        st.session_state.result_data = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Sidebar mejorado
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: var(--text-color); background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ⚙️ Configuración
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        student_id = st.text_input(
            "👤 ID del Estudiante", 
            placeholder="Ej: EST12345",
            help="Ingresa el identificador único del estudiante"
        )
        
        exam_type = st.selectbox(
            "📚 Tipo de Examen",
            ["Matemáticas", "Ciencias", "Historia", "Inglés", "Programación", "Medicina", "Otro"],
            help="Selecciona la categoría del examen"
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="background: var(--card-bg); padding: 1rem; border-radius: 10px; margin: 1rem 0; border: 1px solid var(--border-color);">
            <h4 style="margin: 0 0 0.5rem 0; color: var(--text-color);">💡 Consejos para mejores resultados:</h4>
            <ul style="margin: 0; padding-left: 1.2rem; color: #718096; font-size: 0.9rem;">
                <li>Imagen bien iluminada</li>
                <li>Marcas con X claramente visibles</li>
                <li>Todo el examen en el marco</li>
                <li>Evitar sombras y reflejos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Área principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "📤 Sube la imagen del examen",
            type=['png', 'jpg', 'jpeg'],
            help="Selecciona una imagen clara del examen completado"
        )
    
    with col2:
        st.markdown("""
        <div style="background: var(--card-bg); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border-color);">
            <h3 style="margin: 0 0 1rem 0; color: var(--text-color);">📸 Guía de Captura</h3>
            <div style="color: #718096;">
                <p>✅ <strong>Imagen nítida</strong></p>
                <p>✅ <strong>X bien marcadas</strong></p>
                <p>✅ <strong>Enfoque correcto</strong></p>
                <p>✅ <strong>Buena iluminación</strong></p>
                <p>✅ <strong>Sin reflejos</strong></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar vista previa
    if uploaded_file and not st.session_state.processing:
        st.markdown("""
        <div class="section-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            👀 Vista Previa del Examen
        </div>
        """, unsafe_allow_html=True)
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True, caption="Imagen cargada para evaluación")
    
    # Botón de procesamiento
    if uploaded_file and student_id and not st.session_state.processing:
        if st.button("🚀 Iniciar Evaluación con IA", type="primary", use_container_width=True):
            st.session_state.processing = True
            st.session_state.processed = False
            
            with st.spinner("🔄 Procesando examen con inteligencia artificial... Esto puede tomar 30-60 segundos"):
                result = scanner.process_image(uploaded_file, student_id, exam_type)
                
                if result:
                    st.session_state.result_data = result
                    st.session_state.processed = True
                    st.session_state.processing = False
                    st.rerun()
                else:
                    st.session_state.processing = False
                    st.error("❌ Falló el procesamiento del examen")
    
    # Mostrar resultados si ya se procesó
    if st.session_state.processed and st.session_state.result_data:
        display_results(st.session_state.result_data)
        
        st.markdown("---")
        if st.button("🔄 Evaluar Nuevo Examen", use_container_width=True):
            # Resetear estado
            for key in ['processed', 'result_data', 'processing']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()