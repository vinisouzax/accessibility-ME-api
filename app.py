from flask import Flask, jsonify, request
from os import environ
import xml.etree.ElementTree as ET
import math
import string
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')

errosGeral = []
parent_map = {}
arq = ""
criterio = ""
nivel = ""
link = ""
colors_map = {}

app = Flask(__name__)

app.config['APP_URL'] = environ.get('APP_URL')

@app.route('/accessibility', methods=['POST'])
def analyze():
    global errosGeral, parent_map, arq, criterio, nivel, link, colors_map
    errosGeral = []
    files = request.files.getlist("files")
    manifest = request.files.getlist("manifest")
    color = request.files.getlist("color")

    for c in color:
        c.save(c.filename)
        tree = ET.parse(c.filename)
        arq = c.filename
        colors_map = {}
        colors_map = {c:p for p in tree.iter() for c in p}

    for file in files:
        file.save(file.filename)
        tree = ET.parse(file.filename)
        arq = file.filename
        parent_map = {}
        parent_map = {c:p for p in tree.iter() for c in p}
        for c, p in parent_map.items():
            criterio = "1.1.1 - Conteúdo não textual"
            nivel = "A"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/non-text-content.html"
            criterio111(c)

            criterio = "1.3.1 - Informações e Relações"
            nivel = "A"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/info-and-relationships.html"
            criterio111(c)

            criterio = "1.3.5 - Identifique o propósito da entrada"
            nivel = "AAA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/identify-input-purpose.html"
            criterio135(p)

            criterio = "3.3.5 - Ajuda"
            nivel = "AAA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/help.html"
            criterio135(p)

            criterio = "1.4.3 - Contraste Mínimo"
            nivel = "AA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html"
            criterio143(c, p)

            criterio = "1.4.6 - Contraste Aprimorado"
            nivel = "AAA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/contrast-enhanced.html"
            criterio146(c, p)

            criterio = "1.4.8 - Apresentação Visual"
            nivel = "AAA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/visual-presentation.html"
            criterio148(c)

            criterio = "1.4.11 Contraste sem texto"
            nivel = "AA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html"
            criterio1411(c, p)

            criterio = "2.5.1 - Gestos de ponteiros"
            nivel = "A"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/pointer-gestures.html"
            criterio251(c)

            criterio = "2.5.5 - Tamanho do Alvo"
            nivel = "AAA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/target-size.html"
            criterio255(c, p)

            criterio = "4.1.1 - Análise"
            nivel = "A"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/parsing.html"
            criterio411(c)

    for m in manifest:
        arq = m.filename
        m.save(m.filename)
        tree = ET.parse(m.filename)
        parent_map = {}
        parent_map = {c:p for p in tree.iter() for c in p}
        for c, p in parent_map.items():
            criterio = "1.3.4 - Orientação"
            nivel = "AA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/orientation.html"
            criterio134(c)

            criterio = "2.4.2 - Título de página"
            nivel = "A"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/page-titled.html"
            criterio242(c)

            criterio = "2.4.4 - Objetivo do Link (no Contexto)"
            nivel = "A"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html"
            criterio242(c)

            criterio = "2.4.9 - Objetivo do Link (apenas Link)"
            nivel = "AAA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-link-only.html"
            criterio242(c)

            criterio = "2.4.10 - Títulos de seção"
            nivel = "AAA"
            link = "https://www.w3.org/WAI/WCAG21/Understanding/section-headings.html"
            criterio242(c)

    return response_cors(jsonify({'erros': errosGeral}))

#HABILITA CORS PARA RESPOSTA
def response_cors(response):
    response.headers.add("Access-Control-Allow-Origin", app.config['APP_URL'])
    return response

#Guideline 1.1 Text Alternatives
#1.1.1 Non-text Content
#Level A
#Não foi tratado label para cada input, pois não é necessário em aplicativos móveis
#Todo o conteúdo não textual apresentado ao usuário tem uma alternativa em texto que serve a uma finalidade equivalente

#Guideline 1.1 Adaptável
#1.3.1 Informações e Relações
#Level A
#As informações, a estrutura,e os relacionamentos transmitidos através de apresentação podem ser determinados por meio de código de programação ou 
#estão disponíveis no texto.

def criterio111(child):
    
    #Imagens e botões com imagens com textos alternativos
    #Imagens e botões com imagens com null em contentDescription
    if child.tag == 'ImageView' or child.tag == 'ImageButton':
        if '{http://schemas.android.com/apk/res/android}contentDescription' in child.attrib:
            value = child.attrib['{http://schemas.android.com/apk/res/android}contentDescription'].strip(" ")
            if(value == '@null'):
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Valor nulo na descrição do conteúdo (contentDescription) do componente visual", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})
        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Não há descrição do conteúdo (contentDescription) do componente visual",
                "arq": arq, 
                "link": link, 
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})    
            
    #Inputs de texto em formulários possuem texto descritivo
    #Inputs de texto em formulários possuem texto descritivo não nulo
    elif child.tag == 'EditText':
        if '{http://schemas.android.com/apk/res/android}hint' in child.attrib:
            value = child.attrib['{http://schemas.android.com/apk/res/android}hint'].strip(" ")
            if(value == ''):
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Texto descritivo (hint) em campo de entrada de texto está com valor vazio", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})   

        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                for c, p in parent_map.items():
                    if(c.tag == 'TextView'):
                        if '{http://schemas.android.com/apk/res/android}labelFor' in c.attrib:
                            value = c.attrib['{http://schemas.android.com/apk/res/android}labelFor'].strip(" ")
                            if(value == idComponent):
                                return

            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Não há texto descritivo (hint) em campo de entrada de texto", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})  
            
    #Botões em formulários possuem texto descritivo
    #Botões em formulários possuem texto descritivo não nulo
    elif child.tag == 'Button' or child.tag == 'RadioButton' or child.tag == 'ToggleButton' or child.tag == 'FloatingActionButton':
        if '{http://schemas.android.com/apk/res/android}text' in child.attrib:
            value = child.attrib['{http://schemas.android.com/apk/res/android}text'].strip(" ")
            if(value == ''):
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Texto descritivo (text) em botão está com valor vazio", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Não há texto descritivo (text) em botão", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

    #Itens com onClick e onTouch
    elif '{http://schemas.android.com/apk/res/android}onClick' in child.attrib or '{http://schemas.android.com/apk/res/android}onTouch' in child.attrib:
        verifyItemClicable(child)

    #Itens com clicable=true
    elif '{http://schemas.android.com/apk/res/android}clicable' in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}clicable'].strip(" ")
        if(value == 'true'):
            verifyItemClicable(child)

    #Conteúdo decorativo
    elif '{http://schemas.android.com/apk/res/android}focusable' in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}focusable'].strip(" ")
        childs = findChildsFirstLevel(child)
        if(value == 'true' and len(childs) == 0):
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Possível elemento decorativo que pode receber foco do leitor de tela. Recomenda-se tirar android:focusable='true'", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})

#Função para verificar se item clicável possui alternativa de texto
def verifyItemClicable(child):
    if '{http://schemas.android.com/apk/res/android}contentDescription' in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}contentDescription'].strip(" ")
        if(value == '@null'):
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Valor nulo na descrição do conteúdo (contentDescription) do componente", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})
    elif '{http://schemas.android.com/apk/res/android}text' in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}text'].strip(" ")
        if(value == ''):
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Texto descritivo (text) está com valor vazio", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})  
    else:
        existChild = False
        childs = findChildsFirstLevel(child)
        for c in childs:
            if '{http://schemas.android.com/apk/res/android}contentDescription' in c.attrib:
                value = c.attrib['{http://schemas.android.com/apk/res/android}contentDescription'].strip(" ")
                if(value != '@null'):
                    existChild = True
                    break

            elif '{http://schemas.android.com/apk/res/android}text' in c.attrib:
                value = c.attrib['{http://schemas.android.com/apk/res/android}text'].strip(" ")
                if(value != ''):
                    existChild = True
                    break

        if existChild == False:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Item clicável sem alternativa de texto", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 

##########################

#Guideline 1.4 Distinguível
#1.4.3 Contraste Mínimo
#Level AA
#A apresentação visual do texto e as imagens do texto têm uma taxa de contraste de pelo menos 4,5: 1

#Verifica contraste de texto e fundo
def criterio143(child, parent):

    #Entre fundo e texto do mesmo componente
    if '{http://schemas.android.com/apk/res/android}background' in child.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = child.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 4.5:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

    #Fundo do elemento pai e texto do elemento filho
    elif '{http://schemas.android.com/apk/res/android}background' in parent.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = parent.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 4.5:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  


    #Entre fundo com background tint e texto do mesmo componente
    if '{http://schemas.android.com/apk/res/android}backgroundTint' in child.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = child.attrib['{http://schemas.android.com/apk/res/android}backgroundTint'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 4.5:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

    #Fundo do elemento pai com backgroundTint e texto do elemento filho
    elif '{http://schemas.android.com/apk/res/android}backgroundTint' in parent.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = parent.attrib['{http://schemas.android.com/apk/res/android}backgroundTint'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 4.5:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

##########################

#Guideline 2.5 Modalidades de entrada
#2.5.5 Tamanho do Alvo
#Level AAA
#O tamanho do destino para entradas de ponteiro é de pelo menos 44 por 44 pixels em CSS

def erro_else_parent(child, parent, width_or_height, alt_or_lar, min_wid_or_hei):
    idComponent = ""
    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
    errosGeral.append({"idComponent": idComponent, 
        "criterio": criterio, 
        "nivel": nivel,
        "description": alt_or_lar+" do alvo não é explicitada em dp nem no componente filho "+child.tag+" e nem no(s) componente(s) pai "+parent.tag+
        ". Colocar "+min_wid_or_hei+" com valores de 48dp", 
        "arq": arq, 
        "link": link,
        "component": ET.tostring(child, encoding='utf8').decode('utf8')})

def analyzeParentTamanho(child, parent, width_or_height, alt_or_lar, min_wid_or_hei):
    if '{http://schemas.android.com/apk/res/android}'+width_or_height in parent.attrib:
        value = parent.attrib['{http://schemas.android.com/apk/res/android}'+width_or_height]
        if 'dp' in value:
            value = value.strip('dp').strip(" ")
            if int(value) < 48:
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": alt_or_lar+" do alvo menor que 48dp", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 

        elif '{http://schemas.android.com/apk/res/android}'+min_wid_or_hei in parent.attrib:
            value = parent.attrib['{http://schemas.android.com/apk/res/android}'+min_wid_or_hei]
            if 'dp' in value:
                value = value.strip('dp').strip(" ")
                if int(value) < 48:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": min_wid_or_hei+" do alvo menor que 48dp", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 

            else:
                erro_else_parent(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)
                
        else:
            erro_else_parent(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)

    elif '{http://schemas.android.com/apk/res/android}'+min_wid_or_hei in parent.attrib:
        value = parent.attrib['{http://schemas.android.com/apk/res/android}'+min_wid_or_hei]
        if 'dp' in value:
            value = value.strip('dp').strip(" ")
            if int(value) < 48:
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": min_wid_or_hei+" do alvo menor que 48dp", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 

        else:
            erro_else_parent(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)

    else:
        erro_else_parent(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)

def analyzeTamanhoAlvo(child, parent, width_or_height, alt_or_lar):

    min_wid_or_hei = "android:minWidth" if alt_or_lar == "Largura" else "android:minHeight"

    if '{http://schemas.android.com/apk/res/android}'+width_or_height in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}'+width_or_height]
        if 'dp' in value:
            value = value.strip('dp').strip(" ")
            if int(value) < 48:
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": alt_or_lar+" do alvo menor que 48dp", 
                    "arq": arq,
                    "link": link, 
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 

        elif '{http://schemas.android.com/apk/res/android}'+min_wid_or_hei in child.attrib:
            value = child.attrib['{http://schemas.android.com/apk/res/android}'+min_wid_or_hei]
            if 'dp' in value:
                value = value.strip('dp').strip(" ")
                if int(value) < 48:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": min_wid_or_hei+" do alvo menor que 48dp", 
                        "arq": arq,
                        "link": link, 
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 
            else:
                analyzeParentTamanho(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)
        else:
            analyzeParentTamanho(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)

    elif '{http://schemas.android.com/apk/res/android}'+min_wid_or_hei in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}'+min_wid_or_hei]
        if 'dp' in value:
            value = value.strip('dp').strip(" ")
            if int(value) < 48:
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": min_wid_or_hei+" do alvo menor que 48dp", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 
        else:
            analyzeParentTamanho(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)

    else:
        analyzeParentTamanho(child, parent, width_or_height, alt_or_lar, min_wid_or_hei)

def criterio255(child, parent):
    if child.tag == 'Button' or child.tag == 'RadioButton' or child.tag == 'ToggleButton' or child.tag == 'FloatingActionButton' or child.tag == 'EditText' or child.tag == 'ImageButton':   
        analyzeTamanhoAlvo(child, parent, "layout_width", "Largura")
        analyzeTamanhoAlvo(child, parent, "layout_height", "Altura")
    elif '{http://schemas.android.com/apk/res/android}onClick' in child.attrib or '{http://schemas.android.com/apk/res/android}onTouch' in child.attrib:
        analyzeTamanhoAlvo(child, parent, "layout_width", "Largura")
        analyzeTamanhoAlvo(child, parent, "layout_height", "Altura")

##########################

#Guideline 2.5 Modalidades de entrada
#2.5.1 Gestos de ponteiros
#Level A
#Todas as funcionalidades que usam gestos multiponto ou baseados em caminho para operação podem ser operadas com um único 
#ponteiro sem um gesto baseado em caminho, a menos que um gesto multiponto ou baseado em caminho seja essencial

def criterio251(child):
    if child.tag == 'SeekBar':   
        idComponent = ""
        if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
            idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
        errosGeral.append({"idComponent": idComponent, 
            "criterio": criterio, 
            "nivel": nivel,
            "description": "Está sendo utilizado o componente "+child.tag+". Esse componente exige mais de um gesto, o que pode ocasionar em dificuldades de"+
            " operação para o usuário. Recomenda-se não utilizar esse componente", 
            "arq": arq, 
            "link": link,
            "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 


##########################

#Guideline 2.4 Modalidades de entrada
#2.4.2 Página intitulada
#2.4.10 Título de seção
#Level A
#As páginas possuem títulos que descrevem tópico ou finalidade.

def criterio242(child):
    if child.tag == 'activity':   
        if '{http://schemas.android.com/apk/res/android}label' in child.attrib:
            value = child.attrib['{http://schemas.android.com/apk/res/android}label'].strip(" ")
            if(value == ''):
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}name' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}name']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Essa página possui título descrevendo tópico ou finalidade vazio (android:label)", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 
        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}name' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}name']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Essa página não possui título descrevendo tópico ou finalidade (android:label)", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 


##########################

#Guideline 1.3 Adaptável
#1.3.5 Identifique o propósito da entrada
#Level AA
#Identificar os objetivos dos campos de entrada, adaptando-los para cada propósito.

#Guideline 3.3 Assistência de Entrada
#3.3.5 Ajuda
#Level AAA
#Identificar os objetivos dos campos de entrada, adaptando-los para cada propósito.

def criterio135(child):
    if child.tag == 'EditText':   
        if '{http://schemas.android.com/apk/res/android}inputType' in child.attrib:
            value = child.attrib['{http://schemas.android.com/apk/res/android}inputType'].strip(" ")
            if(value == ''):
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Campo de entrada de texto (EditText) está android:inputType com valor vazio", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 
        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Campo de entrada de texto (EditText) sem android:inputType. "+
                    "Recomenda-se colocar android:inputType a fim de identificar a finalidade desse componente de texto", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 


##########################

#Guideline 1.3 Adaptável
#1.3.4 Orientação
#Level AA
#O conteúdo não restringe sua exibição e operação a uma única orientação da tela

def criterio134(child):
    if child.tag == 'activity':   
        if '{http://schemas.android.com/apk/res/android}screenOrientation' in child.attrib:
            value = child.attrib['{http://schemas.android.com/apk/res/android}screenOrientation']
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}name' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}name']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "O conteúdo desta página está restrito a apenas um tipo de orientação de tela ("+value+")", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 


##########################

#Guideline 1.4 Distinguível
#1.4.6 Contraste Aprimorado
#Level AAA
#A apresentação visual do texto e as imagens do texto têm uma taxa de contraste de pelo menos 7: 1

#Verifica contraste de texto e fundo
def criterio146(child, parent):

    #Entre fundo e texto do mesmo componente
    if '{http://schemas.android.com/apk/res/android}background' in child.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = child.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 7:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 7:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

    #Fundo do elemento pai e texto do elemento filho
    elif '{http://schemas.android.com/apk/res/android}background' in parent.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = parent.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 7:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio,
                        "nivel": nivel, 
                        "description": "Constraste menor que 7:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  


    #Entre fundo com backgroundTint e texto do mesmo componente
    if '{http://schemas.android.com/apk/res/android}backgroundTint' in child.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = child.attrib['{http://schemas.android.com/apk/res/android}backgroundTint'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 7:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 7:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})    

    #Fundo do elemento pai com backgroundTint e texto do elemento filho
    elif '{http://schemas.android.com/apk/res/android}backgroundTint' in parent.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = parent.attrib['{http://schemas.android.com/apk/res/android}backgroundTint'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')

        background = trata_cores(background)
        textColor = trata_cores(textColor)

        if background != None and textColor != None:
            if all(c in string.hexdigits for c in background) and all(c in string.hexdigits for c in textColor):
                arrayB = getArrayRGB(background)
                arrayT = getArrayRGB(textColor)
                ratio = contrast(arrayB, arrayT)
                if ratio < 7:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio,
                        "nivel": nivel, 
                        "description": "Constraste menor que 7:1. Resultado entre cores #"+background+" e #"+textColor+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})   

##########################

#Guideline 1.4 Distinguível
#1.4.8 Apresentação Visual
#Level AAA
#Para a apresentação visual de blocos de texto , um mecanismo está disponível para conseguir o seguinte:
#O texto não é justificado (alinhado às margens esquerda e direita).
#O espaçamento de linha (entrelinha) é de pelo menos um espaço e meio dentro dos parágrafos, e o espaçamento de parágrafo é pelo menos 1,5 vezes maior do que o espaçamento de linha.

def criterio148(child):
    verify_justification(child)
    verify_spacing(child)

#Verifica se texto esta justificado
def verify_justification(child):
    if '{http://schemas.android.com/apk/res/android}text' in child.attrib:
        if '{http://schemas.android.com/apk/res/android}gravity' in child.attrib:
            gravity = child.attrib['{http://schemas.android.com/apk/res/android}gravity']
            if gravity == 'justify':
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Componente com alinhamento justificado", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})  
        elif '{http://schemas.android.com/apk/res/android}layout_gravity' in child.attrib:
            gravity = child.attrib['{http://schemas.android.com/apk/res/android}layout_gravity']
            if gravity == 'justify':
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Componente com alinhamento justificado", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})  
        elif '{http://schemas.android.com/apk/res/android}textAlignment' in child.attrib:
            gravity = child.attrib['{http://schemas.android.com/apk/res/android}textAlignment']
            if gravity == 'justify':
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Componente com alinhamento justificado", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 

#Verifica se espaçamento entre linhas dentro do paragráfo é de 1.5
def verify_spacing(child):
    if '{http://schemas.android.com/apk/res/android}text' in child.attrib:
        if '{http://schemas.android.com/apk/res/android}lineSpacingMultiplier' in child.attrib:
            gravity = float(child.attrib['{http://schemas.android.com/apk/res/android}lineSpacingMultiplier'])
            if gravity != 1.5:
                idComponent = ""
                if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                    idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                errosGeral.append({"idComponent": idComponent, 
                    "criterio": criterio, 
                    "nivel": nivel,
                    "description": "Espaçamento entre linhas dentro do paragráfo não é de 1,5", 
                    "arq": arq, 
                    "link": link,
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 

        elif '{http://schemas.android.com/apk/res/android}layout_gravity' in child.attrib:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": criterio, 
                "nivel": nivel,
                "description": "Não tem espaçamento entre linhas dentro do paragráfo", 
                "arq": arq, 
                "link": link,
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

##########################

#Guideline 4.1 Compatível
#4.1.1 Análise
#Level A
#No conteúdo implementado utilizando linguagens de marcação, os elementos dispõem de tags completas de início e de fim, os elementos são aninhados 
#de acordo com as respectivas especificações, os elementos não contêm atributos duplicados, e quaisquer IDs são exclusivos, exceto quando as especificações 
#permitem estas características.

def criterio411(child):
    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
        idChild = child.attrib['{http://schemas.android.com/apk/res/android}id']
        qtd = 0
        for c, p in parent_map.items():
            if '{http://schemas.android.com/apk/res/android}id' in c.attrib:
                idC = c.attrib['{http://schemas.android.com/apk/res/android}id']
                if idChild == idC:
                    if qtd > 0:
                        errosGeral.append({"idComponent": idChild, 
                            "criterio": criterio, 
                            "nivel": nivel,
                            "description": "IDs duplicados", 
                            "arq": arq, 
                            "link": link,
                            "component": ET.tostring(child, encoding='utf8').decode('utf8')})  
                    qtd = qtd + 1

##########################

#Guideline 1.4 Distinguível
#1.4.11 Contraste sem texto
#Level AA
#A apresentação visual do seguinte tem uma relação de contraste de pelo menos 3: 1 contra as cores adjacentes

#Verifica contraste de fundos entre elemento pai e filho
def criterio1411(child, parent):

    #Fundo do elemento pai e fundo do elemento filho
    if '{http://schemas.android.com/apk/res/android}background' in parent.attrib and '{http://schemas.android.com/apk/res/android}background' in child.attrib:
        backgroundP = parent.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        backgroundC = child.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')

        backgroundP = trata_cores(backgroundP)
        backgroundC = trata_cores(backgroundC)

        if backgroundP != None and backgroundC != None:
            if all(c in string.hexdigits for c in backgroundP) and all(c in string.hexdigits for c in backgroundC):
                arrayB = getArrayRGB(backgroundP)
                arrayT = getArrayRGB(backgroundC)
                ratio = contrast(arrayB, arrayT)
                if ratio < 3:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 3:1. Resultado entre cores #"+backgroundP+" e #"+backgroundC+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

    #Fundo do elemento pai com backgroundTint e fundo do elemento filho com backgroundTint
    if '{http://schemas.android.com/apk/res/android}backgroundTint' in parent.attrib and '{http://schemas.android.com/apk/res/android}backgroundTint' in child.attrib:
        backgroundP = parent.attrib['{http://schemas.android.com/apk/res/android}backgroundTint'].lstrip('#')
        backgroundC = child.attrib['{http://schemas.android.com/apk/res/android}backgroundTint'].lstrip('#')

        backgroundP = trata_cores(backgroundP)
        backgroundC = trata_cores(backgroundC)

        if backgroundP != None and backgroundC != None:
            if all(c in string.hexdigits for c in backgroundP) and all(c in string.hexdigits for c in backgroundC):
                arrayB = getArrayRGB(backgroundP)
                arrayT = getArrayRGB(backgroundC)
                ratio = contrast(arrayB, arrayT)
                if ratio < 3:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": criterio, 
                        "nivel": nivel,
                        "description": "Constraste menor que 3:1. Resultado entre cores #"+backgroundP+" e #"+backgroundC+" = "+str(ratio)+":1", 
                        "arq": arq, 
                        "link": link,
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

##########################

#Funções Genéricas

def trata_cores(cor):
    if "color/" in cor:
        cor_aux = cor.split("color/")
        for c, p in colors_map.items():
            if c.tag == 'color':   
                if 'name' in c.attrib:
                    value = c.attrib['name'].strip(" ")
                    if(value == cor_aux[1]):
                        return c.text.lstrip('#')
    else:
        return cor


def calc_luminanace(v):
    v /= 255
    return  (v / 12.92) if (v <= 0.03928) else (pow( (v + 0.055) / 1.055, 2.4 ))
                
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
    lv = len(hexColor)
    if lv == 1:
        v = int(hexColor, 16)*17
        rgb = v, v, v
    elif lv == 3:
        rgb = tuple(int(hexColor[i:i+1], 16)*17 for i in range(0, 3))
    else:
        rgb = tuple(int(hexColor[i:i+lv//3], 16) for i in range(0, lv, lv//3))
    array = []
    array.append(rgb)
    array = [x for xs in array for x in xs]
    return array

def findParents(child):
    parents = []
    exists = False
    while True:
        for c, p in parent_map.items():
            if child == c:
                parents.append(p)
                exists = True
                child = p
                break
            else:
                exists = False
        if(exists == False):
            break
    return parents

def findChilds(parent):
    childs = []
    i = j = 0
    while True:
        for c, p in parent_map.items():
            if parent == p:
                childs.append(c)
                i+=1
        if i == j:
            break
        else:
            parent = childs[j]
            j+=1
    
    return childs

def findChildsFirstLevel(parent):
    childs = []
    for c, p in parent_map.items():
        if parent == p:
            childs.append(c)
    return childs

##########################

#BACKUP

def analyzeParentsTamanho(child, width_or_height, alt_or_lar, min_wid_or_hei):
    parents = findParents(child)
    tags = "" 
    for p in parents:
        if '{http://schemas.android.com/apk/res/android}'+width_or_height in p.attrib:
            value = p.attrib['{http://schemas.android.com/apk/res/android}'+width_or_height]
            if 'dp' in value:
                value = value.strip('dp').strip(" ")
                if int(value) < 48:
                    idComponent = ""
                    if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                        idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                    errosGeral.append({"idComponent": idComponent, 
                        "criterio": '2.5.5 - Tamanho do Alvo', 
                        "description": alt_or_lar+" do alvo menor que 48dp", 
                        "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 
                    return
                else:
                    return
            else:
                tags += p.tag+", "

        else:
            tags += p.tag+", "

    if tags != "":
        idComponent = ""
        if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
            idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
        errosGeral.append({"idComponent": idComponent, 
            "criterio": '2.5.5 - Tamanho do Alvo', 
            "description": alt_or_lar+" do alvo não é explicitada em dp nem no componente filho "+child.tag+" e nem no(s) componente(s) pai "+tags+
            ". Colocar "+min_wid_or_hei+" com valores de 48dp", 
            "component": ET.tostring(child, encoding='utf8').decode('utf8')})

if __name__ == '__main__':
    app.run(debug=True)


