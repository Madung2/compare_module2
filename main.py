import streamlit as st
from docx import Document
import json
from lxml import etree
import zipfile
import pandas as pd
def highlight_text(text):
    # highlighted_text = text.replace(word, f"<mark style='background-color: yellow'>{word}</mark>")
    return f"<mark style='background-color: yellow'>{text}</mark>"

st.set_page_config(layout="wide")
st.title("약정서-의견서 비교")
def reorganize_result(result):
    """
    주어진 result 리스트에서 'table' 타입을 직전의 'text' 타입 항목 밑에 추가합니다.
    - result: [{'type': 'text', 'res': ...}, {'type': 'table', 'res': ...}] 형태의 리스트
    """
    reorganized = []
    for item in result:
        if item['type'] == 'table' and reorganized:
            # 직전의 'text' 항목에 'table'을 키로 추가
            last_item = reorganized[-1]
            if last_item['type'] == 'text':
                # 'table'을 새로운 키로 추가
                last_item['table'] = item['res']
            else:
                # 만약 직전 항목이 'text'가 아니라면 단독으로 추가
                reorganized.append(item)
        else:
            # 'text' 항목은 그대로 추가
            reorganized.append(item)
    return reorganized
def create_text_table_mapping(result):
    """
    주어진 result 리스트에서 'text'의 res를 키로 하고, 다음 'table'의 res를 값으로 하는 딕셔너리를 생성합니다.
    - result: [{'type': 'text', 'res': ...}, {'type': 'table', 'res': ...}] 형태의 리스트
    """
    mapping = {}
    previous_text = None

    for item in result:
        if item['type'] == 'text':
            # 'text' 항목을 키로 설정
            previous_text = item['res']
        elif item['type'] == 'table' and previous_text is not None:
            # 'table' 항목을 이전 'text' 키의 값으로 설정
            mapping[previous_text] = item['res']
            previous_text = None  # 다음 'table'이 연속해서 붙지 않도록 초기화

    return mapping
def read_opinion(file_path):
    """
    .docx 파일에서 텍스트와 표를 순서대로 추출하여 반환합니다.
    - file_path: .docx 파일 경로
    """
    # .docx 파일을 ZIP 형식으로 열기
    """
    .docx 파일에서 텍스트와 표를 순서대로 추출하여 반환합니다.
    - file_path: .docx 파일 경로
    """
    # .docx 파일을 ZIP 형식으로 열기
    with zipfile.ZipFile(file_path) as docx_zip:
        # 'word/document.xml' 파일을 읽기
        with docx_zip.open('word/document.xml') as xml_file:
            # XML 파싱
            tree = etree.parse(xml_file)
            root = tree.getroot()
            
            # XML 네임스페이스 설정
            nsmap = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }
            
            result = []  # 텍스트와 테이블을 순서대로 저장할 리스트
            in_table = False  # 현재 테이블 내 텍스트인지 확인하기 위한 플래그
            
            # 문서의 모든 요소를 순회하며 처리
            for elem in root.iter():
                # 테이블 시작 (w:tbl 태그)
                if elem.tag == f"{{{nsmap['w']}}}tbl":
                    in_table = True
                    table_data = []
                    for row in elem.findall('.//w:tr', namespaces=nsmap):
                        row_data = [cell.text for cell in row.findall('.//w:t', namespaces=nsmap) if cell.text]
                        table_data.append(row_data)
                    result.append({'type': 'table', 'res': table_data})
                    in_table = False  # 테이블 처리 완료 후 플래그 해제

                # 문단 처리 (w:p 태그)
                elif elem.tag == f"{{{nsmap['w']}}}p" and not in_table:
                    # 테이블 내부가 아닌 경우에만 텍스트 추출
                    text = ''.join(e.text for e in elem.iter() if e.text).strip()
                    if text:
                        result.append({'type': 'text', 'res': text})

    res = create_text_table_mapping(result)

    return res
def read_docx(file):
    doc = Document(file)
    content = {}
    current_title = None
    
    for para in doc.paragraphs:
        # Check if all runs in the paragraph are bold
        if para.text.strip():  # Ensure paragraph has non-whitespace text
            is_all_bold = all(run.bold for run in para.runs if run.text.strip())
            if is_all_bold:
                # Treat this paragraph as a title
                current_title = para.text.strip()
                content[current_title] = []  # Create a new entry for this title
            elif current_title:
                # Add text under the current title
                content[current_title].append(para.text.strip())

    # Optionally, remove empty entries or clean up
    content = {k: [v for v in values if v] for k, values in content.items() if k}

    return content


def compare_texts(text1, text2,json_input): # text1 = 약정서 text2=의겨넛
    # 간단한 예시로 차이점을 보여줍니다. 필요에 따라 로직을 커스터마이징할 수 있습니다.
    """text1은 줄별로 된 str 리스트 """

    res =[]
    for  k, v in json_input.items():
        contract_block = v['contract']['block']
        opinion_block = v['opinion']['block']
        contract_syn = v['contract']['syn']
        opinion_syn = v['opinion']['syn']

        #text1 먼저 처리 
        con_res ={}

        for k, v in text1.items():
 
            if any(b in k for b in contract_block):  # 조건을 수정하여 올바르게 루프 확인
                for line in v:
                    if any(s in line for s in contract_syn):  # 조건을 수정하여 올바르게 확인
                        con_res = {
                            'all_text': v,
                            'target': line
                        }
                        break
                         # 조건에 맞으면 루프를 종료
        op_res = {}
        print('text2', text2)
        for key, table in text2.items():

            if any(b in key for b in opinion_block):  # opinion_block 내 키 확인
                

                

                    # table이 리스트의 리스트 형식이라고 가정
                df = pd.DataFrame(table)  # DataFrame 생성
                print('df' , df)

                html_table = df.to_html(index=False, escape=False)  # DataFrame을 HTML로 변환

                # for row in table:
                #     if len(row) > 1 and any(row[0] in s for s in opinion_syn):  # 첫 번째 열과 비교
                #         # [1] 번째 값을 하이라이트 처리
                #         highlighted_target = f"<mark style='background-color: yellow'>{row[1]}</mark>"
                for s in opinion_syn:
                    if s in html_table:
                        op_res = {
                            'all_text': html_table,  # HTML로 변환된 표를 추가
                            # 'highlighted': highlighted_target,
                            'target': s
                        }

        res.append([con_res, op_res])
    
    print('rrrrrrrrrrrrrrrrrrrrrr')
    print(res)
    return res        
        
    # if text1 == text2:
    #     return "두 문서는 동일합니다."
    # else:
    #     return "두 문서에 차이가 있습니다."



# 텍스트 입력 필드 - 화면 상단에 위치
default_json = """
{
    "차주" : {
        "contract": {"block":["대출계약서"], "syn":["차주"], "res_type":"ORG"},
        "opinion" : {"block":["신청내용"], "syn":["차주"] }
    },
    "상환방법" : {
        "contract": {"block":["대출금의 상환"], "syn":["일시", "분할"] },
        "opinion" : {"block":["신청내용"], "syn":["만기"] }
    }
}
"""
# default_json = """
# {
#     "차주" : {
#         "contract": {"block":["대출계약서"], "syn":["차주"] },
#         "opinion" : {"block":["대출신청조건"], "syn":["차주"] }
#     }
# }
# """

def highlight_target_in_html(html_content, target):
    """
    HTML 문자열에서 target 텍스트를 하이라이트합니다.
    - html_content: 원본 HTML 문자열
    - target: 하이라이트할 텍스트
    """
    # target 텍스트를 하이라이트하는 HTML 태그로 감싸기
    highlighted_html = html_content.replace(
        target,
        f"<mark style='background-color: yellow'>{target}</mark>"
    )
    return highlighted_html
# JSON 입력 필드 - 화면 상단에 위치
json_input = st.text_area("JSON 비교 기준 입력:", value=default_json, height=300)
# JSON 파싱
try:
    json_input = json.loads(json_input)
except json.JSONDecodeError:
    st.error("올바른 JSON 형식이 아닙니다. 입력을 확인하세요.")
    json_input = None

# 약정서 업로드
st.header("1. 약정서 업로드")
agreement_file = st.file_uploader("약정서 파일을 업로드하세요 (docx)", type=["docx"], key="agreement")

# 의견서 업로드
st.header("2. 의견서 업로드")
opinion_file = st.file_uploader("의견서 파일을 업로드하세요 (docx)", type=["docx"], key="opinion")

st.markdown('***')
if agreement_file is not None and opinion_file is not None:
    # 파일 읽기
    agreement_text = read_docx(agreement_file)
    opinion_text = read_opinion(opinion_file)


    # 문서 비교
    st.header("3. 문서 비교 결과")
    comparison_result = compare_texts(agreement_text, opinion_text, json_input)  # [[con, op], [con, op]]
    for index, (con, op) in enumerate(comparison_result):
        # 두 개의 열(column)을 생성
        col1, col2 = st.columns(2)

        # 좌측 - con 내용 표시
        with col1:
            st.subheader("약정서 내용")

            if isinstance(con, dict) and 'all_text' in con and 'target' in con:

                for idx, text in enumerate(con['all_text'], start=1):
                    if text == con['target']:
                        # target 문장에 하이라이트 적용
                        highlighted_target = highlight_text(text)
                        st.markdown(f"{idx}. {highlighted_target}", unsafe_allow_html=True)
                    else:
                        # 일반 텍스트는 번호와 함께 표시
                        st.markdown(f"{idx}. {text}")
            else:
                st.text_area("약정서", con, height=200, key=f"con_{index}")  # 고유 키 추가

        # 우측 - op 내용 표시
        with col2:
            st.subheader("의견서 내용")
            if isinstance(op, dict):

                if isinstance(op, dict) and 'all_text' in op :
                # op['all_text']가 HTML이므로 HTML로 렌더링

                    for t in op['target']:
                        if t in op['all_text']:
                            highlighted_html = highlight_target_in_html(op['all_text'],t)
                            print('hilighted')
                            print(highlighted_html)
                            st.markdown(highlighted_html, unsafe_allow_html=True)
                            break
                        else:
                            st.markdown(op['all_text'],unsafe_allow_html=True)
                elif isinstance(op, dict):
                    st.markdown(op,unsafe_allow_html=True)

            else:
                st.text_area("의견서", op, height=200, key=f"op_{index}")  # 고유 키 추가

else:
    st.warning("두 파일을 모두 업로드하세요.")