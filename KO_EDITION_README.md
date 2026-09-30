# 국문판 v2.0 소스 — 《생성형 AI를 감당할 수 있는가: 국가 간 균일한 가격과 불균등한 부담》

*Korean edition of "Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens" (English version 2.0). The English text is the original; the numbers, tables and figures are the same.*

## 무엇이 들어 있나

- `paper_ko/`: 국문판 LaTeX 소스(`main.tex`), 참고문헌(`references.bib`, `apalike-doi.bst`), 표 본문(`tables/`), 그림(`figures/`), 컴파일된 PDF(`main.pdf`, 34쪽)와 빌드 기록.
- 국문판을 만들고 검증하는 스크립트:
  - `revision_audit/build_revision_tables_ko.py`: v2.0 표 7개의 국문 본문을 영문 본문에서 만든다. 행 이름만 바꾸며, 다른 칸이 하나라도 다르면 멈춘다(`--check`는 쓰지 않고 대조만 한다).
  - `revision_audit/figure_price_ratio_ko.py`: 그림 3(Go/Plus 가격비) 국문판.
  - `verification/en_ko_number_check.py`: 국문판과 영문판에 적힌 숫자를 절마다 대조한다. 영문 본문의 숫자는 666개다. 월 이름이나 수사("nine plans" = "9개 요금제")처럼 언어 때문에 생기는 차이 55개는 이유와 함께 목록에 적었다. 그 밖의 차이가 있으면 실패한다.
  - `code/30_figures.py`: 그림 6 국문 범례만 고쳤다("AI 이용자/인터넷 이용자 비율").
  - `code/40_tables_tex.py`: 표 10의 국문 표본 이름 "군집"을 "합침"으로 고쳤다("군집"은 군집 표준오차와 헷갈린다). 영문 표는 그대로다.
  - `code/50_make_docx.py`: Word 변환. v2.0 표 머리글과 국문 정리·명제 이름을 반영했고, 그림은 `pdftoppm`으로 변환한다.
  - `build_papers.sh`, `run_revision.sh`, `check_release.sh`, `README.md`, `verification/README.md`: 위 스크립트와 국문 빌드를 파이프라인에 연결했고, 변경 내역과 검증 기록을 적었다.

번역문은 다른 검토자가 영문과 문단 단위로 대조했고, 그 지적(뜻이 뒤집혀 읽힐 수 있는 문장 1개, 사소한 표현·용어 18개)을 모두 반영했다. 영문 원고, 자료, 분석 결과는 바뀌지 않았다. 영문 PDF 3종(식별본·익명본·표지)은 v2.0과 바이트 단위로 같다.

## 적용하는 법

재현성 패키지 v2.0.1에는 이 내용이 이미 들어 있다. v2.0 패키지(https://doi.org/10.5281/zenodo.23057976)에서 시작할 때만 이 파일들을 같은 경로로 덮어쓴다. 국문판까지 다시 만들어 확인하려면 다음을 실행한다.

```bash
bash run_revision.sh --analysis-only   # 분석, 표 본문, 그림 3, 숫자 대조(영문 292곳, 영·국문 29개 부분)
bash build_papers.sh                   # 영문 PDF 3종과 국문 PDF
bash check_release.sh                  # PDF가 소스보다 오래되지 않았는지 등 점검
```

2026년 10월 1일에 이 순서대로 확인했다. 국문 PDF는 여기 든 `paper_ko/main.pdf`와 바이트 단위로 같았고, 영문 PDF 3종은 v2.0과 같았으며, `check_release.sh`를 통과했다.

국문 PDF만 다시 만들려면 `paper_ko`에서 `xelatex main && bibtex main && xelatex main && xelatex main`을 실행한다. TeX Live의 xelatex와 xetexko, Noto Serif/Sans CJK KR 글꼴, Liberation 글꼴이 필요하다.

Word 파일은 `python code/50_make_docx.py ko 파일명.docx`로 만든다. pandoc 3.1, python-docx, poppler-utils가 필요하다. PDF가 기준본이고, Word 파일은 편의를 위한 사본이다.

## 상태

2026년 10월 1일 재현성 패키지 v2.0.1로 Zenodo에 올렸다(전체 버전 DOI https://doi.org/10.5281/zenodo.23006365). 영문 원고와 자료·분석 결과는 v2.0 그대로다. v2.0 패키지에는 이전(v1.8) 국문 원고가 보관되어 있다.
