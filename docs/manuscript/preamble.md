# Manuscript typography

```latex
\usepackage{graphicx}
\usepackage{listings}
\renewenvironment{quote}{\list{}{\rightmargin\leftmargin}\item\relax\begin{minipage}{\linewidth}}{\end{minipage}\endlist}
\setcitestyle{authoryear,round,semicolon}
\definecolor{BFLink}{HTML}{235F5A}
\hypersetup{colorlinks=true,linkcolor=BFLink,citecolor=BFLink,urlcolor=BFLink}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{remark}[theorem]{Remark}
\newtheorem{example}[theorem]{Example}
\let\BFcontents\tableofcontents
\renewcommand{\tableofcontents}{}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\setlength{\emergencystretch}{3em}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
```
