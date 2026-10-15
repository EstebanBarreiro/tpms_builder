========================================================================
TPMS Builder - Guía de Instalación y Uso
========================================================================

Autor: Esteban Barreiro (Desarrollado con la asistencia de Google Gemini)
Versión: 1.2.0
Compatibilidad: Blender 5.2 LTS (o superior)

------------------------------------------------------------------------
DESCRIPCIÓN GENERAL
------------------------------------------------------------------------
TPMS Builder es una herramienta procedimental diseñada para la 
generación de entramados geométricos complejos (lattices) y superficies 
mínimas triplemente periódicas (TPMS). Permite envolver y adaptar 
automáticamente estructuras estancas (manifold) a la geometría de cualquier 
objeto 3D activo, optimizando modelos para manufactura aditiva e impresión 3D.

Este add-on fue creado inspirado en el trabajo open source de campos (f13lds) 
de Matthew Shomper y su enfoque procedimental dentro de Blender.

------------------------------------------------------------------------
REQUISITOS PREVIOS
------------------------------------------------------------------------
1. Blender 5.2 LTS (o superior).
2. Librería 'scikit-image' instalada en el entorno Python de Blender
   (necesaria para el algoritmo de Marching Cubes en estructuras TPMS).

------------------------------------------------------------------------
INSTRUCCIONES DE INSTALACIÓN
------------------------------------------------------------------------
1. Descarga el archivo `.zip` del add-on.
2. Abre Blender y ve a Edit > Preferences > Add-ons.
3. Haz clic en el botón 'Install...' (o 'Get Extensions' / menú desplegable superior) 
   y selecciona el archivo `.zip` descargado.
4. Activa la casilla de verificación junto a "Add Mesh: F13LD TPMS Builder".
5. Una vez activado, abre la vista 3D y despliega la barra lateral presionando 
   la tecla 'N'. Encontrarás la pestaña dedicada bajo el nombre 'F13LD TPMS'.

------------------------------------------------------------------------
FUNCIONALIDADES PRINCIPALES
------------------------------------------------------------------------
* Arquitectura Dual:
  - BCC (Body-Centered Cubic): Generación geométrica pura de puntales
    cilíndricos continuos mediante modificadores Skin y Subsurf.
  - TPMS Volumétrico: Generación por campos escalares (Gyroid, 
    Schwarz Primitive y Schwarz Diamond).

* Gyroid Radial Adaptativo:
  Transformación de coordenadas cilíndricas ajustada dinámicamente al
  origen local del objeto activo, permitiendo que el entramado acompañe
  la curvatura de piezas complejas y arcos.

* Gradiente de Porosidad Procedimental:
  Modulación continua del grosor de pared y radio de los puntales a lo
  largo del eje Z (de arriba hacia abajo), permitiendo variar la densidad
  y resistencia mecánica del modelo.

* Modo Previsualización (LOD):
  Sistema de baja resolución o densidad reducida para iterar parámetros
  visualmente en segundos antes de ejecutar el cálculo final.

* Selector de Algoritmo Booleano (Boolean Solver):
  Permite alternar entre 'Float' (Rápido / Estable, ideal para mallas Skin 
  e iteraciones rápidas) y 'Exact' (Preciso) directamente desde la interfaz.

------------------------------------------------------------------------
NOTAS DE USO
------------------------------------------------------------------------
- Selecciona siempre un objeto MESH activo antes de presionar "Generar Estructura".
- Para mallas complejas o derivadas del modificador Skin (BCC), se recomienda
  mantener el 'Algoritmo Booleano' en 'Float' para evitar colapsos de geometría.
- Alternar el 'Algoritmo Booleano' entre 'Manifold/Exact' en caso de ser necesario.
- Ajusta el punto pivot (origen) de tu modelo para controlar el centro de 
  emisión de la estructura cuando utilices 'Gyroid Radial'.
========================================================================