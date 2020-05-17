from flask import Flask, jsonify, request
import xml.etree.ElementTree as ET
import math
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')

erros = []
componenteErros = []
componenteIdErros = []
errosDsc = []

app = Flask(__name__)


@app.route('/accessibility', methods=['POST'])
def analyze():
    global erros, componenteErros, componenteIdErros, errosDsc
    erros = []
    componenteErros = []
    componenteIdErros = []
    errosDsc = []
    files = request.files.getlist("files")
    for file in files:
        tree = ET.parse(file.filename)
        parent_map = {c:p for p in tree.iter() for c in p}
        for c, p in parent_map.items():
            criterio111(c)
            criterio143(c, p)
            criterio255(c, p)

    return jsonify({'erros': erros, 
    'componenteErros': componenteErros, 
    'componenteIdErros': componenteIdErros,
    'errosDsc': errosDsc
    }), 200


#Guideline 1.1 Text Alternatives
#1.1.1 Non-text Content
#Level A
#Não foi tratado label para cada input, pois não é necessário em aplicativos móveis

def criterio111(element):
    
    #Imagens e botões com imagens com textos alternativos
    #Imagens e botões com imagens com null em contentDescription
    if element.tag == 'ImageView' or element.tag == 'ImageButton':
        if '{http://schemas.android.com/apk/res/android}contentDescription' in element.attrib:
            value = element.attrib['{http://schemas.android.com/apk/res/android}contentDescription']
            if(value == '@null'):
                componenteErros.append(ET.tostring(element, encoding='utf8').decode('utf8'))
                if '{http://schemas.android.com/apk/res/android}id' in element.attrib:
                    componenteIdErros.append(element.attrib['{http://schemas.android.com/apk/res/android}id'])
                erros.append('1.1.1 - Conteúdo não textual')
                errosDsc.append("Valor nulo na descrição do conteúdo (contentDescription) do componente visual")
        else:
            componenteErros.append(ET.tostring(element, encoding='utf8').decode('utf8'))
            if '{http://schemas.android.com/apk/res/android}id' in element.attrib:
                componenteIdErros.append(element.attrib['{http://schemas.android.com/apk/res/android}id'])
            erros.append('1.1.1 - Conteúdo não textual')
            errosDsc.append("Não há descrição do conteúdo (contentDescription) do componente visual")
            
    #Inputs de texto em formulários possuem texto descritivo
    #Inputs de texto em formulários possuem texto descritivo não nulo
    if element.tag == 'EditText':
        if '{http://schemas.android.com/apk/res/android}hint' in element.attrib:
            value = element.attrib['{http://schemas.android.com/apk/res/android}hint']
            if(value == ''):
                componenteErros.append(ET.tostring(element, encoding='utf8').decode('utf8'))
                if '{http://schemas.android.com/apk/res/android}id' in element.attrib:
                    componenteIdErros.append(element.attrib['{http://schemas.android.com/apk/res/android}id'])
                erros.append('1.1.1 - Conteúdo não textual')
                errosDsc.append("Texto descritivo (hint) em campo de entrada de texto está com valor vazio")
        else:
            componenteErros.append(ET.tostring(element, encoding='utf8').decode('utf8'))
            if '{http://schemas.android.com/apk/res/android}id' in element.attrib:
                componenteIdErros.append(element.attrib['{http://schemas.android.com/apk/res/android}id'])
            erros.append('1.1.1 - Conteúdo não textual')
            errosDsc.append("Não há texto descritivo (hint) em campo de entrada de texto")
            
    #Botões em formulários possuem texto descritivo
    #Botões em formulários possuem texto descritivo não nulo
    if element.tag == 'Button' or element.tag == 'RadioButton' or element.tag == 'ToggleButton' or element.tag == 'FloatingActionButton':
        if '{http://schemas.android.com/apk/res/android}text' in element.attrib:
            value = element.attrib['{http://schemas.android.com/apk/res/android}text']
            if(value == ''):
                componenteErros.append(ET.tostring(element, encoding='utf8').decode('utf8'))
                if '{http://schemas.android.com/apk/res/android}id' in element.attrib:
                    componenteIdErros.append(element.attrib['{http://schemas.android.com/apk/res/android}id'])
                erros.append('1.1.1 - Conteúdo não textual')
                errosDsc.append("Texto descritivo (text) em botão está com valor vazio")
        else:
            componenteErros.append(ET.tostring(element, encoding='utf8').decode('utf8'))
            if '{http://schemas.android.com/apk/res/android}id' in element.attrib:
                componenteIdErros.append(element.attrib['{http://schemas.android.com/apk/res/android}id'])
            erros.append('1.1.1 - Conteúdo não textual')
            errosDsc.append("Não há texto descritivo (text) em botão")

##########################

#Guideline 1.4 Distinguível
#1.4.3 Contraste Mínimo
#Level AA

def calc_luminanace(v):
    v /= 255
    return  (v / 12.92) if (v <= 0.03928) else (pow( (v + 0.055) / 1.055, 2.4 ));
                
def luminanace(r, g, b):
    r = calc_luminanace(r)
    g = calc_luminanace(g)
    b = calc_luminanace(b)
    return r * 0.2126 + g * 0.7152 + b * 0.0722

def contrast(rgb1, rgb2):
    lum1 = luminanace(rgb1[0], rgb1[1], rgb1[2])
    lum2 = luminanace(rgb2[0], rgb2[1], rgb2[2])
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)

def getArrayRGB(hexColor):
    rgb = tuple(int(hexColor[i:i+2], 16) for i in (0, 2, 4))
    array = []
    array.append(rgb)
    array = [x for xs in array for x in xs]
    return array

def criterio143(child, parent):
    if '{http://schemas.android.com/apk/res/android}background' in child.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = child.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')
        arrayB = getArrayRGB(background)
        arrayT = getArrayRGB(textColor)
        ratio = contrast(arrayB, arrayT)
        if ratio < 4.5:
            componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
            erros.append('1.4.3 - Contraste Mínimo')
            errosDsc.append("Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+ratio+":1")
    elif '{http://schemas.android.com/apk/res/android}background' in parent.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = parent.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')
        arrayB = getArrayRGB(background)
        arrayT = getArrayRGB(textColor)
        ratio = contrast(arrayB, arrayT)
        if ratio < 4.5:
            componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
            erros.append('1.4.3 - Contraste Mínimo')
            errosDsc.append("Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+ratio+":1")

##########################

#Guideline 2.5 Modalidades de entrada
#2.5.5 Tamanho do Alvo
#Level AAA

def analyzeTamanhoAlvo(child, parent, width_or_height, alt_or_lar):
    if '{http://schemas.android.com/apk/res/android}'+width_or_height in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}'+width_or_height]
        if 'match_parent' in value or 'fill_parent' in value or 'wrap_content' in value:
            if '{http://schemas.android.com/apk/res/android}'+width_or_height in parent.attrib:
                value = parent.attrib['{http://schemas.android.com/apk/res/android}'+width_or_height]
                if 'dp' in value:
                    value = value.lstrip('dp').strip(" ")
                    if int(value) < 48:
                        componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
                        if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                            componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
                        erros.append('2.5.5 - Tamanho do Alvo')
                        errosDsc.append(alt_or_lar+" do alvo menor que 48dp")
                else:
                    componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
                    erros.append('2.5.5 - Tamanho do Alvo')
                    errosDsc.append(alt_or_lar+" do alvo não é explicitada nem no componente filho "+child.tag+" e nem no componente pai "+parent.tag)
            else:
                componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
                erros.append('2.5.5 - Tamanho do Alvo')
                errosDsc.append(alt_or_lar+" do alvo não é explicitada nem no componente filho "+child.tag+" e nem no componente pai "+parent.tag)             
        elif 'dp' in value:
            value = value.lstrip('dp').strip(" ")
            if int(value) < 48:
                componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
                erros.append('2.5.5 - Tamanho do Alvo')
                errosDsc.append(alt_or_lar+" do alvo menor que 48dp")
        else:
            componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
            erros.append('2.5.5 - Tamanho do Alvo')
            errosDsc.append(alt_or_lar+" do alvo não é explicitada em dp")
    else:
        if '{http://schemas.android.com/apk/res/android}'+width_or_height in parent.attrib:
            value = parent.attrib['{http://schemas.android.com/apk/res/android}'+width_or_height]
            if 'match_parent' in value or 'fill_parent' in value or 'wrap_content' in value:
                componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
                erros.append('2.5.5 - Tamanho do Alvo')
                errosDsc.append(alt_or_lar+" do alvo não é explicitada nem no componente filho "+child.tag+" e nem no componente pai "+parent.tag)
            elif 'dp' in value:
                value = value.lstrip('dp').strip(" ")
                if int(value) < 48:
                    componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
                    erros.append('2.5.5 - Tamanho do Alvo')
                    errosDsc.append(alt_or_lar+" do alvo menor que 48dp")
            else:
                componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
                erros.append('2.5.5 - Tamanho do Alvo')
                errosDsc.append(alt_or_lar+" do alvo não é explicitada em dp nem no componente filho "+child.tag+" e nem no componente pai "+parent.tag)         
        else:
            componenteErros.append(ET.tostring(child, encoding='utf8').decode('utf8'))
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                componenteIdErros.append(child.attrib['{http://schemas.android.com/apk/res/android}id'])
            erros.append('2.5.5 - Tamanho do Alvo')
            errosDsc.append(alt_or_lar+" do alvo não é explicitada nem no componente filho "+child.tag+" e nem no componente pai "+parent.tag) 

def criterio255(child, parent):
    if child.tag == 'Button' or child.tag == 'RadioButton' or child.tag == 'ToggleButton' or child.tag == 'FloatingActionButton' or child.tag == 'EditText' or child.tag == 'ImageButton':   
        analyzeTamanhoAlvo(child, parent, "layout_width", "Largura")
        analyzeTamanhoAlvo(child, parent, "layout_height", "Altura")

##########################

if __name__ == '__main__':
    app.run(debug=True)
