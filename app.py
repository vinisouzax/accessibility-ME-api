from flask import Flask, jsonify, request
import xml.etree.ElementTree as ET
import math
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')

errosGeral = []
parent_map = {}

app = Flask(__name__)


@app.route('/accessibility', methods=['POST'])
def analyze():
    global errosGeral, parent_map
    errosGeral = []
    files = request.files.getlist("files")
    manifest = request.files.getlist("manifest")
    for file in files:
        file.save(file.filename)
        tree = ET.parse(file.filename)
        parent_map = {}
        parent_map = {c:p for p in tree.iter() for c in p}
        for c, p in parent_map.items():
            criterio111(c)
            criterio135(p)
            criterio143(c, p)
            criterio146(c, p)
            criterio251(c)
            criterio255(c, p)

    for m in manifest:
        m.save(m.filename)
        tree = ET.parse(m.filename)
        parent_map = {}
        parent_map = {c:p for p in tree.iter() for c in p}
        for c, p in parent_map.items():
            criterio134(c)
            criterio242(c)

    return jsonify({'erros': errosGeral}), 200


#Guideline 1.1 Text Alternatives
#1.1.1 Non-text Content
#Level A
#Não foi tratado label para cada input, pois não é necessário em aplicativos móveis
#Todo o conteúdo não textual apresentado ao usuário tem uma alternativa em texto que serve a uma finalidade equivalente

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
                    "criterio": '1.1.1 - Conteúdo não textual', 
                    "description": "Valor nulo na descrição do conteúdo (contentDescription) do componente visual", 
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})
        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.1.1 - Conteúdo não textual', 
                "description": "Não há descrição do conteúdo (contentDescription) do componente visual", 
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
                    "criterio": '1.1.1 - Conteúdo não textual', 
                    "description": "Texto descritivo (hint) em campo de entrada de texto está com valor vazio", 
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})   

        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
                for c in parent_map.items():
                    if(c.tag == 'TextView'):
                        if '{http://schemas.android.com/apk/res/android}labelFor' in c.attrib:
                            value = c.attrib['{http://schemas.android.com/apk/res/android}labelFor'].strip(" ")
                            if(value == idComponent):
                                return

            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.1.1 - Conteúdo não textual', 
                "description": "Não há texto descritivo (hint) em campo de entrada de texto", 
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
                    "criterio": '1.1.1 - Conteúdo não textual', 
                    "description": "Texto descritivo (text) em botão está com valor vazio", 
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.1.1 - Conteúdo não textual', 
                "description": "Não há texto descritivo (text) em botão", 
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
                "criterio": '1.1.1 - Conteúdo não textual', 
                "description": "Possível elemento decorativo que pode receber foco do leitor de tela. Recomenda-se tirar android:focusable='true'", 
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
                "criterio": '1.1.1 - Conteúdo não textual', 
                "description": "Valor nulo na descrição do conteúdo (contentDescription) do componente", 
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})
    elif '{http://schemas.android.com/apk/res/android}text' in child.attrib:
        value = child.attrib['{http://schemas.android.com/apk/res/android}text'].strip(" ")
        if(value == ''):
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.1.1 - Conteúdo não textual', 
                "description": "Texto descritivo (text) está com valor vazio", 
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
                "criterio": '1.1.1 - Conteúdo não textual', 
                "description": "Item clicável sem alternativa de texto", 
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
        arrayB = getArrayRGB(background)
        arrayT = getArrayRGB(textColor)
        ratio = contrast(arrayB, arrayT)
        if ratio < 4.5:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.4.3 - Contraste Mínimo', 
                "description": "Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+ratio+":1", 
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

    #Fundo do elemento pai e texto do elemento filho
    elif '{http://schemas.android.com/apk/res/android}background' in parent.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = parent.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')
        arrayB = getArrayRGB(background)
        arrayT = getArrayRGB(textColor)
        ratio = contrast(arrayB, arrayT)
        if ratio < 4.5:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.4.3 - Contraste Mínimo', 
                "description": "Constraste menor que 4,5:1. Resultado entre cores #"+background+" e #"+textColor+" = "+ratio+":1", 
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
        "criterio": '2.5.5 - Tamanho do Alvo', 
        "description": alt_or_lar+" do alvo não é explicitada em dp nem no componente filho "+child.tag+" e nem no(s) componente(s) pai "+parent.tag+
        ". Colocar "+min_wid_or_hei+" com valores de 48dp", 
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
                    "criterio": '2.5.5 - Tamanho do Alvo', 
                    "description": alt_or_lar+" do alvo menor que 48dp", 
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
                        "criterio": '2.5.5 - Tamanho do Alvo', 
                        "description": min_wid_or_hei+" do alvo menor que 48dp", 
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
                    "criterio": '2.5.5 - Tamanho do Alvo', 
                    "description": min_wid_or_hei+" do alvo menor que 48dp", 
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
                    "criterio": '2.5.5 - Tamanho do Alvo', 
                    "description": alt_or_lar+" do alvo menor que 48dp", 
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
                        "criterio": '2.5.5 - Tamanho do Alvo', 
                        "description": min_wid_or_hei+" do alvo menor que 48dp", 
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
                    "criterio": '2.5.5 - Tamanho do Alvo', 
                    "description": min_wid_or_hei+" do alvo menor que 48dp", 
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
            "criterio": '2.5.1 - Gestos de ponteiros', 
            "description": "Está sendo utilizado o componente "+child.tag+". Esse componente exige mais de um gesto, o que pode ocasionar em dificuldades de"+
            " operação para o usuário. Recomenda-se não utilizar esse componente", 
            "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 


##########################

#Guideline 2.4 Modalidades de entrada
#2.4.2 Página intitulada
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
                    "criterio": '2.4.2 - Página intitulada', 
                    "description": "Essa página possui título descrevendo tópico ou finalidade vazio (android:label)", 
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 
        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}name' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}name']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '2.4.2 - Página intitulada', 
                "description": "Essa página não possui título descrevendo tópico ou finalidade (android:label)", 
                "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 


##########################

#Guideline 1.3 Adaptável
#1.3.5 Identifique o propósito da entrada
#Level AA
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
                    "criterio": '1.3.5 - Identifique o propósito da entrada', 
                    "description": "Campo de entrada de texto (EditText) está android:inputType com valor vazio", 
                    "component": ET.tostring(child, encoding='utf8').decode('utf8')}) 
        else:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.3.5 - Identifique o propósito da entrada', 
                "description": "Campo de entrada de texto (EditText) sem android:inputType. "+
                    "Recomenda-se colocar android:inputType a fim de identificar a finalidade desse componente de texto", 
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
                "criterio": '1.3.4 - Orientação', 
                "description": "O conteúdo desta página está restrito a apenas um tipo de orientação de tela ("+value+")", 
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
        arrayB = getArrayRGB(background)
        arrayT = getArrayRGB(textColor)
        ratio = contrast(arrayB, arrayT)
        if ratio < 7:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.4.6 - Contraste Máximo', 
                "description": "Constraste menor que 7:1. Resultado entre cores #"+background+" e #"+textColor+" = "+ratio+":1", 
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

    #Fundo do elemento pai e texto do elemento filho
    elif '{http://schemas.android.com/apk/res/android}background' in parent.attrib and '{http://schemas.android.com/apk/res/android}textColor' in child.attrib:
        background = parent.attrib['{http://schemas.android.com/apk/res/android}background'].lstrip('#')
        textColor = child.attrib['{http://schemas.android.com/apk/res/android}textColor'].lstrip('#')
        arrayB = getArrayRGB(background)
        arrayT = getArrayRGB(textColor)
        ratio = contrast(arrayB, arrayT)
        if ratio < 7:
            idComponent = ""
            if '{http://schemas.android.com/apk/res/android}id' in child.attrib:
                idComponent = child.attrib['{http://schemas.android.com/apk/res/android}id']
            errosGeral.append({"idComponent": idComponent, 
                "criterio": '1.4.6 - Contraste Máximo', 
                "description": "Constraste menor que 7:1. Resultado entre cores #"+background+" e #"+textColor+" = "+ratio+":1", 
                "component": ET.tostring(child, encoding='utf8').decode('utf8')})  

##########################

#Funções Genéricas

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
    rgb = tuple(int(hexColor[i:i+2], 16) for i in (0, 2, 4))
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


