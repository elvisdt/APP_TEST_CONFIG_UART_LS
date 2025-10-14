from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Archivo de salida
out_pdf = "plano_prensa_20T_doble_piston.pdf"

# Crear lienzo A3 apaisado
c = canvas.Canvas(out_pdf, pagesize=landscape(A3))
width, height = landscape(A3)

# Función auxiliar para cotas
def dibujar_cota(x1, y1, x2, y2, texto):
    c.line(x1, y1, x2, y2)
    c.line(x1, y1, x1+3*mm, y1+2*mm)
    c.line(x1, y1, x1+3*mm, y1-2*mm)
    c.line(x2, y2, x2-3*mm, y2+2*mm)
    c.line(x2, y2, x2-3*mm, y2-2*mm)
    c.setFont("Helvetica", 8)
    c.drawCentredString((x1+x2)/2, (y1+y2)+4*mm, texto)

# Marco exterior
margen = 10*mm
c.rect(margen, margen, width-2*margen, height-2*margen)

# Títulos de vistas
c.setFont("Helvetica-Bold", 12)
c.drawCentredString(width/4, height-20*mm, "VISTA FRONTAL")
c.drawCentredString(width/2, height-20*mm, "VISTA LATERAL")
c.drawCentredString(3*width/4, height-20*mm, "VISTA SUPERIOR (PLANTA)")

# Escala y dimensiones
escala = 0.15
alto_total = 2000  # mm
ancho_total = 1000 # mm
profundidad_total = 800 # mm

# ===== Vista Frontal =====
x0, y0 = 50*mm, 60*mm
c.rect(x0, y0, 120*mm*escala, 200*mm*escala)  # Bastidor
c.rect(x0+40*mm*escala, y0+20*mm*escala, 40*mm*escala, 5*mm*escala)  # Platino inferior
c.rect(x0+30*mm*escala, y0+140*mm*escala, 10*mm*escala, 30*mm*escala)  # Cilindro 1
c.rect(x0+80*mm*escala, y0+140*mm*escala, 10*mm*escala, 30*mm*escala)  # Cilindro 2
c.rect(x0+25*mm*escala, y0+130*mm*escala, 70*mm*escala, 10*mm*escala)  # Platino superior
dibujar_cota(x0, y0-10*mm, x0+120*mm*escala, y0-10*mm, "1000 mm")
dibujar_cota(x0+130*mm*escala, y0, x0+130*mm*escala, y0+200*mm*escala, "2000 mm")

# ===== Vista Lateral =====
x0, y0 = 150*mm, 60*mm
c.rect(x0, y0, 80*mm*escala, 200*mm*escala)  # Bastidor
c.rect(x0+20*mm*escala, y0+140*mm*escala, 10*mm*escala, 30*mm*escala)
c.rect(x0+50*mm*escala, y0+140*mm*escala, 10*mm*escala, 30*mm*escala)
c.rect(x0+15*mm*escala, y0+130*mm*escala, 50*mm*escala, 10*mm*escala)
c.rect(x0+25*mm*escala, y0+20*mm*escala, 30*mm*escala, 5*mm*escala)
dibujar_cota(x0, y0-10*mm, x0+80*mm*escala, y0-10*mm, "800 mm")
dibujar_cota(x0+90*mm*escala, y0, x0+90*mm*escala, y0+200*mm*escala, "2000 mm")

# ===== Vista Superior (Planta) =====
x0, y0 = 250*mm, 60*mm
c.rect(x0, y0, 100*mm*escala, 80*mm*escala)  # Bastidor
c.rect(x0+20*mm*escala, y0+20*mm*escala, 10*mm*escala, 10*mm*escala)  # Cilindro 1
c.rect(x0+70*mm*escala, y0+20*mm*escala, 10*mm*escala, 10*mm*escala)  # Cilindro 2
dibujar_cota(x0, y0-10*mm, x0+100*mm*escala, y0-10*mm, "1000 mm")
dibujar_cota(x0-10*mm, y0, x0-10*mm, y0+80*mm*escala, "800 mm")

# Cajetín
c.setFont("Helvetica-Bold", 10)
c.rect(width-80*mm, margen, 70*mm, 40*mm)
c.drawString(width-78*mm, margen+35*mm, "Proyecto: Prensa hidráulica 20T - doble pistón")
c.setFont("Helvetica", 8)
c.drawString(width-78*mm, margen+28*mm, "Autor: Calixto Solorzano Holsen")
c.drawString(width-78*mm, margen+22*mm, "Curso: Mecánico de mantenimiento")
c.drawString(width-78*mm, margen+16*mm, "Escala: 1:20")
c.drawString(width-78*mm, margen+10*mm, "Fecha: 2025-09-29")

# Guardar PDF
c.showPage()
c.save()

print(f"Plano generado: {out_pdf}")