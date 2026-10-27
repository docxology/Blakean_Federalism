# Manuscript typography

```latex
\usepackage{graphicx}
\usepackage{needspace}
\usepackage{listings}
\renewenvironment{quote}{\list{}{\rightmargin\leftmargin}\item\relax\begin{minipage}{\linewidth}\itshape}{\end{minipage}\endlist}
\setcitestyle{authoryear,round,semicolon}
\definecolor{BFLink}{HTML}{B00020}
\hypersetup{colorlinks=true,linkcolor=BFLink,citecolor=BFLink,urlcolor=BFLink}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{remark}[theorem]{Remark}
\newtheorem{example}[theorem]{Example}
\makeatletter
\renewcommand{\l@subsection}{\@dottedtocline{2}{1.5em}{3em}}
\makeatother
\let\BFOriginalContents\tableofcontents
\newcommand{\BFcontents}{\begingroup\fontsize{8}{8.5}\selectfont\setlength{\parskip}{0pt}\BFOriginalContents\endgroup}
\renewcommand{\tableofcontents}{}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\setlength{\emergencystretch}{3em}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
```
