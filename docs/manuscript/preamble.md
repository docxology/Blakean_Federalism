# Manuscript typography

```latex
\usepackage{graphicx}
\usepackage{needspace}
\usepackage{etoolbox}
\ifnum{{ANALYTICAL_ABSTRACTS}}=1\relax
\AtBeginDocument{\floatplacement{figure}{H}}
\AtEndEnvironment{titlepage}{\par\vspace{4pt}{\small\raggedright\textbf{Graphical abstract 1.} {{COVER_ABSTRACT_CAPTION}}\par}}
\fi
\usepackage{listings}
\captionsetup[figure]{font=small,labelfont=bf,justification=raggedright,singlelinecheck=false,skip=6pt}
\renewenvironment{quote}{%
  \list{}{%
    \setlength{\leftmargin}{1.8em}%
    \setlength{\rightmargin}{1em}%
    \setlength{\topsep}{4pt plus 1pt minus 1pt}%
    \setlength{\partopsep}{0pt}%
    \setlength{\parsep}{0pt}}%
  \item\relax\begin{minipage}{\linewidth}\itshape
}{\end{minipage}\endlist\nopagebreak[4]}
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
\newcommand{\BFcontents}{\floatplacement{figure}{tbp}\begingroup\fontsize{8}{8}\selectfont\setlength{\parskip}{0pt}\BFOriginalContents\endgroup}
\renewcommand{\tableofcontents}{}
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000
\setlength{\emergencystretch}{3em}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
```
