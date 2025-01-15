from svglib import svglib
from reportlab.graphics import renderPDF

file_path = 'C:/Users/12199/Desktop/DEGA/00_Latex/paper0108/fig'
input_name = 'firefighting.svg'
output_name = 'firefighting.pdf'

# 读取 SVG 文件
drawing = svglib.svg2rlg(f'{file_path}/{input_name}')

# 将 SVG 转换为 PDF
renderPDF.drawToFile(drawing, f'{file_path}/{output_name}')
