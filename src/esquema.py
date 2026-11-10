"""Esquema de los archivos de entrada: campos, tipo de dato y uso en el reporte.

Es la única definición de la estructura esperada. La usan la validación de calidad
(calidad.py), la lectura (generar_reporte.py) y el diccionario de datos
(generar_diccionario.py). Para agregar o cambiar un campo, edita solo este archivo.

Cada campo se escribe como:  NOMBRE | tipo | nulos | uso | descripción
  tipo   entero, decimal, decimal 0-1, decimal 0-100, texto, monto o texto, fecha, fecha texto,
         id modelo, lista de id, o "categoría: valor 1; valor 2"
  nulos  "sí" si el campo puede venir vacío
  uso    "R" si el reporte lo necesita (el proceso se detiene si falta la columna),
         "-" si es informativo
"""
from dataclasses import dataclass, field

AMBIENTES = "categoría: PRODUCTIVO; NO PRODUCTIVO; MIXTO; EN REVISIÓN; Sin información"
COBERTURA = "categoría: Coberturado; No Coberturado"
CALIFICACION = "categoría: Satisfactorio; Aceptable; Regular; Deficiente"


@dataclass
class Campo:
    nombre: str
    tipo: str
    nulos: bool
    requerido: bool
    descripcion: str

    @property
    def categorias(self):
        return [c.strip() for c in self.tipo.split(":", 1)[1].split(";")] if self.tipo.startswith("categoría:") else None


@dataclass
class Archivo:
    clave: str            # nombre en config.yaml
    titulo: str
    granularidad: str
    id_modelo: str        # columna que identifica al modelo; "" si no tiene
    fecha: str            # columna con la fecha del archivo; "" si no tiene
    seccion: str          # sección del reporte que alimenta
    texto: str
    campos: list = field(default_factory=list)

    def __post_init__(self):
        for linea in self.texto.strip().splitlines():
            nombre, tipo, nulos, uso, desc = (p.strip() for p in linea.split("|"))
            self.campos.append(Campo(nombre, tipo, nulos == "sí", uso == "R", desc))

    @property
    def requeridos(self):
        return [c.nombre for c in self.campos if c.requerido]

    @property
    def nombres(self):
        return [c.nombre for c in self.campos]


ARCHIVOS = {a.clave: a for a in [
    Archivo("input_principal", "Input principal histórico", "Una fila por modelo y fecha de corte", "ID_MODELO", "FECHA",
            "Todas", f"""
FECHA | fecha | no | R | Fecha de corte, fin de mes
ID_MODELO | id modelo | no | R | Identificador del modelo. Llave de unión con los demás archivos
NOMBRE_MODELO | texto | no | R | Nombre del modelo
TIER_MODELO | categoría: I; II; III; IV | no | R | Nivel de materialidad
ESTADO_MODELO | texto | no | R | Estado del modelo a la fecha de corte
TIPO_RIESGO | texto | no | R | Tipo de riesgo
PRODUCTO | texto | no | R | Producto
SUB_PRODUCTO | texto | no | R | Sub producto
BANCA | texto | no | R | Banca
PROCESO | texto | no | R | Proceso en el que se usa el modelo
ESTADO_SEGUIMIENTO | categoría: Con Seguimiento; Sin Seguimiento; No aplica; Sin información | no | R | Situación del seguimiento
ESTADO_ALERTA | categoría: En alerta; Sin alerta; Saludable; Aceptable; No aplica; Sin información | no | R | Alerta de salud del modelo
EXCESO_MESES_TTM | decimal | sí | R | Meses de exceso sobre el tiempo máximo de atención; negativo si aún está en plazo
EXCEDE_TTM | categoría: Excede TTM; No excede; No tiene TTM | sí | R | Situación frente al tiempo máximo de atención
IMPACTO | monto o texto | sí | R | Impacto estimado de la alerta: un monto o un texto como "Sin info"
PRESENCIA_MITIGANTE | categoría: Si; No | sí | R | Indica si la alerta tiene mitigante temporal
DESCRIPCION_MITIGANTE | texto | sí | R | Descripción del mitigante
VALIDACION_COMPLETA | categoría: Con validación; Sin validación | no | R | Validación de primera vez
VALIDACION_PERIODICA | categoría: Coberturado; Descoberturado | no | R | Vigencia de la validación periódica
NOTA_DINAMICA_VALIDACION | decimal 0-1 | sí | R | Nota dinámica de validación
OBS_CRIT_RELE_MODE_PENDIENTES_VI | entero | no | R | Observaciones de validación críticas, relevantes y moderadas pendientes
OBS_CRIT_RELE_MODE_VENCIDAS_VI | entero | no | R | Observaciones de validación críticas, relevantes y moderadas vencidas
OBS_SBS_AI_PENDIENTES | entero | no | R | Observaciones de SBS y auditoría interna pendientes
OBS_SBS_AI_VENCIDAS | entero | no | R | Observaciones de SBS y auditoría interna vencidas
PLATAFORMA_IMPLEMENTACION | texto | no | R | Plataformas de implementación, separadas por coma
AMBIENTE_DESPLIEGUE | {AMBIENTES} | no | R | Ambiente del despliegue
PLATAFORMA_DATA | texto | no | R | Plataformas de data, separadas por coma
AMBIENTE_DATA | {AMBIENTES} | no | R | Ambiente de la data
RATIO_IMPLEMENTACION | decimal 0-1 | sí | R | Parte del despliegue en ambiente productivo
RATIO_DATA | decimal 0-1 | sí | R | Parte de la data en ambiente productivo
OBS_AMB_TEC_PENDIENTES | entero | no | R | Observaciones de entorno tecnológico pendientes
OBS_AMB_TEC_VENCIDOS | entero | no | R | Observaciones de entorno tecnológico vencidas
BBDD | decimal 0-1 | sí | R | Completitud de seguimiento: base de datos
GOB | decimal 0-1 | sí | R | Completitud de seguimiento: gobierno
PRECISION_DISCRIMINACION | decimal 0-1 | sí | R | Completitud de seguimiento: precisión y discriminación
GRANULARIDAD | decimal 0-1 | sí | R | Completitud de seguimiento: granularidad
UNIVARIADA | decimal 0-1 | sí | R | Completitud de seguimiento: análisis univariado
NUM_INCIDENTES | entero | no | R | Incidentes en el inventario
NOTA_GOBIERNO | decimal 0-1 | sí | R | Nota de documentación y gobierno
NOTA_10_LINEAMIENTOS | decimal 0-1 | sí | R | Cumplimiento de los 10 lineamientos de desarrollo
NOTA_CALIDAD_DATOS | decimal 0-1 | sí | R | Indicador de calidad de datos
MODEL_DEVELOPER | texto | no | R | Área desarrolladora
RESPONSABLE_MONITORING | texto | no | R | Responsable del seguimiento
RESPONSABLE_DEVELOPER | texto | no | R | Responsable del desarrollo
PO_USUARIO | texto | no | R | PO o usuario responsable
MODEL_USER | texto | no | R | Área usuaria
"""),
    Archivo("inventario", "Inventario de modelos", "Una fila por modelo", "ID_MODELO", "",
            "Inventario", """
ID_MODELO | id modelo | no | R | Identificador del modelo
CODIGO_MODELO | texto | no | - | Código del modelo
NOMBRE_MODELO | texto | no | R | Nombre del modelo
PERIMETRO_MODELO | texto | no | R | Perímetro: modelo, módulo, proceso, etc.
ESTADO_MODELO | texto | sí | - | Estado en el inventario. El reporte usa el estado del input principal
TIER_MODELO | texto | sí | - | Nivel de materialidad
ENTIDAD_MODELO | texto | no | - | Entidad dueña del modelo
CLASE_MODELO | texto | sí | - | Clase de riesgo
TIPO_MODELO | texto | sí | R | Tipo de modelo
USO_GENERICO_MODELO | texto | sí | - | Uso genérico
USO_ESPECIFICO_1 | texto | sí | - | Uso específico principal
USO_ESPECIFICO_2 | texto | sí | - | Uso específico secundario
BANCA | texto | sí | - | Banca
LINEA_PRODUCTO | texto | sí | - | Línea de producto
ID_MODELO_INPUT | lista de id | sí | R | Modelos que este modelo usa como insumo, separados por punto y coma
COD_NOMBRE_MODELO_INPUT | texto | sí | - | Código y nombre de los modelos insumo
ID_VERSION_ANTERIOR | id modelo | sí | - | Versión anterior del modelo
CODIGO_MODELO_VERSION_ANTERIOR | texto | sí | - | Código de la versión anterior
NOMBRE_MODELO_VERSION_ANTERIOR | texto | sí | - | Nombre de la versión anterior
MODEL_IMPLEMENTER | texto | sí | - | Área implementadora
MODEL_USER | texto | sí | - | Área usuaria
MODEL_DEVELOPER | texto | sí | - | Área desarrolladora
MODEL_VALIDATOR | texto | sí | - | Área validadora
MODEL_DATA_PROVIDER | texto | sí | - | Área proveedora de datos
MODELOELIMINADO | entero | no | - | Marca de eliminación. Su significado está por confirmar
DESCRIPCION | texto | sí | - | Descripción del modelo
FECHA_INICIO_USO | fecha | sí | - | Fecha de inicio de uso
FECHA_RETIRO_USO | fecha | sí | - | Fecha de retiro
"""),
    Archivo("ttm", "TTM", "Una fila por modelo en alerta", "ID_MODELO", "",
            "Seguimiento", """
ID_MODELO | id modelo | no | R | Identificador del modelo
NOMBRE_MODELO | texto | no | - | Nombre del modelo
TIER | texto | no | - | Nivel de materialidad
FECH_ALERTA | fecha | no | R | Fecha en que se levantó la alerta
DIAGNOSTICO | texto | sí | R | Diagnóstico de la alerta
PLAN_ACCION | texto | sí | R | Plan de acción
MITIGANTE | texto | sí | - | Mitigante temporal
TTM_GOBIERNO_MESES | decimal | sí | R | Tiempo máximo de atención definido por gobierno, en meses
TTM_REAL_HOY | decimal | no | R | Tiempo transcurrido, en meses
HOLGURA_EXCESO_TTM | decimal | sí | R | TTM real menos TTM de gobierno; positivo si excede
SOLICITO_AMPLIACION | categoría: Si; No | no | R | Indica si se pidió ampliar el plazo
NUEVA_FECH_SUBSANACION | fecha | sí | R | Nueva fecha comprometida
COMENTARIOS | texto | sí | R | Comentarios
"""),
    Archivo("observaciones", "Reporte de observaciones", "Una fila por observación de validación pendiente", "ID_Model",
            "FECHA_PROCESO", "Observaciones", """
FECHA_PROCESO | fecha | no | R | Fecha del archivo
ID_Obs | entero | no | R | Identificador de la observación
Observación | texto | no | R | Texto de la observación
Recomendación | texto | no | R | Recomendación
Criticidad_observacion | categoría: Crítico; Relevante; Moderado; Bajo; Potencial; Nulo | no | R | Criticidad
Ambito_observacion | texto | no | R | Ámbito
Estado_observacion | texto | no | - | Estado de la observación
Estado_Vencimiento | categoría: Vencido; Por vencer < 15 días; Por vencer < 30 días; Por vencer > 30 días | no | R | Situación del plazo
# Ampliaciones | entero | no | R | Número de ampliaciones de plazo
Fecha ampliada | fecha | sí | R | Nuevo compromiso tras una ampliación
Fecha cierre | fecha | sí | - | Fecha de cierre
Fecha estimada | fecha | no | R | Compromiso original
Codigo_proyecto | texto | no | - | Código del proyecto de validación
Nombre_proyecto | texto | no | R | Proyecto de validación
Estado_proyecto | texto | no | - | Estado del proyecto
Tipo_revisión | texto | no | R | Tipo de revisión
ID_Model | id modelo | no | R | Identificador del modelo
Codigo_modelo | texto | no | - | Código del modelo
Nombre_modelo | texto | no | - | Nombre del modelo
Tier | texto | no | - | Nivel de materialidad
Area homologada | texto | no | R | Área responsable
Manager_nombre | texto | no | R | Manager de validación
Validador_nombre | texto | no | R | Validador
Propietario_nombre | texto | no | R | Propietario de la observación
Diferencia_dias | entero | sí | - | Días desde el compromiso original
Observaciones_PA_createdon | fecha | no | - | Fecha de registro
"""),
    Archivo("observaciones_sbs_ai", "Observaciones SBS & AI", "Una fila por observación de SBS o auditoría interna",
            "ID_MODELO", "", "Observaciones", """
ID | entero | no | R | Identificador de la observación
CodigoProyecto | texto | no | R | Código del proyecto u oficio
NombreProyecto/Visita Inspección | texto | no | R | Proyecto o visita de inspección
TituloObs | texto | no | R | Título de la observación
Observación | texto | no | R | Texto de la observación
Recomendación | texto | no | R | Recomendación
Estado | categoría: Pendiente; En Proceso; Implementada Por Verificar | no | R | Estado. Solo "Pendiente" cuenta como pendiente
Riesgo | texto | no | R | Nivel de riesgo. SBS y auditoría interna usan escalas distintas
Fecha Emisión | fecha texto | no | R | Fecha de emisión, como dd/mm/aaaa
Fecha de Vencimiento | fecha | no | R | Fecha de vencimiento
Propietario | texto | no | R | Propietario
Unidad Responsable | texto | no | R | Unidad responsable
Número de ampliaciones | entero | no | R | Ampliaciones de plazo
Tipo | categoría: SBS; A. Interna | no | R | Origen de la observación
Correo | texto | sí | - | Correo del propietario. No se incluye en el reporte
ID_MODELO | lista de id | sí | R | Modelos a los que aplica; texto si es transversal
NOMBRE_MODELO | texto | sí | - | Nombre del modelo
"""),
    Archivo("nota_gobierno", "Nota de Gobierno", "Una fila por PO usuario y model developer", "", "",
            "Gobierno", """
MODELO_DEVELOPER | texto | no | R | Área desarrolladora
MODEL_USER | texto | no | R | Área usuaria
PO_USUARIO | texto | no | R | PO o usuario responsable. Llave de unión, junto con el model developer
NOTA_GOBIERNO | decimal 0-100 | no | R | Nota de gobierno: promedio de los componentes con dato
NOTA_POLITICAS | decimal 0-100 | sí | R | Componente: políticas
NOTA_ESTANDARES | decimal 0-100 | sí | R | Componente: estándares
NOTA_DESARROLLO | decimal 0-100 | sí | R | Componente: desarrollo
NOTA_VALIDACION | decimal 0-100 | sí | R | Componente: validación
WAIVERS | decimal 0-100 | sí | R | Componente: waivers
NOTA_CUMPL_CALCULADORA_VALIZACION | decimal 0-100 | sí | R | Componente: uso de la calculadora de valorización
"""),
    Archivo("calidad_datos", "Calidad de Datos", "Una fila por modelo evaluado", "ID", "",
            "Implementación", """
ID | id modelo | no | R | Identificador del modelo
Owner | texto | no | - | Área dueña
Modelo | texto | no | - | Nombre del modelo
Tier | texto | no | - | Nivel de materialidad
Documentación de incidencias por alertas | decimal 0-1 | no | R | Criterio del indicador
Gobierno formal de calidad de datos y umbrales definidos para alertas | decimal 0-1 | no | R | Criterio del indicador
Roles definidos y atención a alertas en calidad de datos | decimal 0-1 | no | R | Criterio del indicador
Notificación de alertas al usuario | decimal 0-1 | no | R | Criterio del indicador
Controles sobre variables insumo del modelo | decimal 0-1 | no | R | Criterio del indicador
Controles sobre variables salida del modelo | decimal 0-1 | no | R | Criterio del indicador
Monitoreo automático o reportes adhoc | decimal 0-1 | no | R | Criterio del indicador
Indicador de Calidad de datos | decimal 0-1 | no | R | Suma de los siete criterios
Rango de cumplimiento | categoría: <= a 50%; 50% a 70%; > a 70% | no | R | Rango del indicador
"""),
    Archivo("coberturas", "Tablón de coberturas", "Una fila por modelo", "Modelo_ID", "Fecha",
            "Validación", f"""
Fecha | fecha | no | R | Fecha del archivo
Modelo_ID | id modelo | no | R | Identificador del modelo
Nombre_Modelo | texto | no | - | Nombre del modelo
Codigo_Modelo | texto | no | - | Código del modelo
Estado_Modelo | texto | no | - | Estado del modelo
Perímetro | texto | no | - | Perímetro
Tier | texto | no | - | Nivel de materialidad
Imp_Codigo_proyecto | texto | sí | - | Último proyecto de validación de implementación: código
Imp_Nombre_proyecto | texto | sí | - | Último proyecto de validación de implementación: nombre
Imp_Fecha_fin | fecha | sí | R | Fecha fin del proyecto de implementación
Imp_Estado_proyecto | texto | no | - | Estado del proyecto de implementación
Imp_Tipo_revision | texto | no | R | Tipo de revisión de implementación
Imp_Manager | texto | sí | R | Manager de la validación de implementación
Imp_Validador | texto | sí | R | Validador de implementación
Imp_Alcance | texto | sí | R | Alcance de la validación de implementación
Met_Codigo_proyecto | texto | sí | - | Último proyecto de validación metodológica: código
Met_Nombre_proyecto | texto | sí | - | Último proyecto de validación metodológica: nombre
Met_Fecha_fin | fecha | sí | R | Fecha fin del proyecto metodológico
Met_Estado_proyecto | texto | no | - | Estado del proyecto metodológico
Met_Tipo_revision | texto | no | R | Tipo de revisión metodológica
Cobertura_Metodologia | {COBERTURA} | no | R | Cobertura del frente metodológico
Cobertura_Implementación | {COBERTURA} | no | R | Cobertura del frente de implementación
Cobertura_Global | categoría: Coberturado; Descoberturado | no | R | Coberturado solo si ambos frentes lo están
Met_Manager | texto | sí | R | Manager de la validación metodológica
Met_Validador | texto | sí | R | Validador metodológico
Met_Alcance | texto | sí | R | Alcance de la validación metodológica
Fecha_descobertura_Met | fecha texto | sí | R | Fecha en que vence la cobertura metodológica, como dd/mm/aaaa
Proy_Cobertura_Met | {COBERTURA} | no | R | Cobertura metodológica proyectada
Fecha_descobertura_Imp | fecha texto | sí | R | Fecha en que vence la cobertura de implementación, como dd/mm/aaaa
Proy_Cobertura_Imp | {COBERTURA} | no | R | Cobertura de implementación proyectada
Proy_Cobertura_Global | categoría: Coberturado; Descoberturado | no | R | Cobertura global proyectada
Modelos_Cobertura_Perimetro_Q | texto | sí | - | Perímetro considerado en la proyección
Modelos_Cobertura_Tier_Q_1 | texto | sí | - | Tier considerado en la proyección
Calificación_Metodología | {CALIFICACION} | sí | R | Calificación de la última validación metodológica
Calificación_Implementación | {CALIFICACION} | sí | R | Calificación de la última validación de implementación
"""),
]}

# Criterios del indicador de calidad de datos: (columna, etiqueta corta, peso máximo).
# Los pesos se infirieron del máximo observado en el archivo y suman 1. Confirmarlos con el dueño del indicador.
CRITERIOS_CALIDAD = [
    ("Documentación de incidencias por alertas", "Documentación de incidencias", 0.10),
    ("Gobierno formal de calidad de datos y umbrales definidos para alertas", "Gobierno formal y umbrales", 0.20),
    ("Roles definidos y atención a alertas en calidad de datos", "Roles y atención de alertas", 0.20),
    ("Notificación de alertas al usuario", "Notificación al usuario", 0.10),
    ("Controles sobre variables insumo del modelo", "Controles de variables insumo", 0.15),
    ("Controles sobre variables salida del modelo", "Controles de variables salida", 0.20),
    ("Monitoreo automático o reportes adhoc", "Monitoreo automático", 0.05),
]

# Componentes de la nota de gobierno: (columna, etiqueta)
COMPONENTES_GOBIERNO = [
    ("NOTA_POLITICAS", "Políticas"), ("NOTA_ESTANDARES", "Estándares"), ("NOTA_DESARROLLO", "Desarrollo"),
    ("NOTA_VALIDACION", "Validación"), ("WAIVERS", "Waivers"), ("NOTA_CUMPL_CALCULADORA_VALIZACION", "Calculadora"),
]
