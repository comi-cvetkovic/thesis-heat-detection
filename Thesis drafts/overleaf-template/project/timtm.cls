%%
%% This is file `timtm.cls', is a modification of the acmart.cls file taken from
%% the Overleaf project: https://www.overleaf.com/gallery/tagged/acm-official#.WOuOk2e1taQ
%%
%% It has been adapted for the Interactive Media Technology (TIMTM) and Media Management (TMMTM) programmes
%% at KTH Royal Institute of Technology.
%%
%% 2021-11-09 Gerald Q. Maguire Jr. adapted template to KTH's TITM and TMMTM requirements, including:
%% removing the ACM copyright and other notices in the generate documents - as these are not applicable
%% and rewriting some of the contents of the sample document.
%%
%% 2022-07-14 Gerald Q. Maguire Jr. adapted the template to collect
%% the meta data relevant to DiVA - aligning it with the other LaTeX template
%% he wrote.
%%
%% \CharacterTable
%%  {Upper-case    \A\B\C\D\E\F\G\H\I\J\K\L\M\N\O\P\Q\R\S\T\U\V\W\X\Y\Z
%%   Lower-case    \a\b\c\d\e\f\g\h\i\j\k\l\m\n\o\p\q\r\s\t\u\v\w\x\y\z
%%   Digits        \0\1\2\3\4\5\6\7\8\9
%%   Exclamation   \!     Double quote  \"     Hash (number) \#
%%   Dollar        \$     Percent       \%     Ampersand     \&
%%   Acute accent  \'     Left paren    \(     Right paren   \)
%%   Asterisk      \*     Plus          \+     Comma         \,
%%   Minus         \-     Point         \.     Solidus       \/
%%   Colon         \:     Semicolon     \;     Less than     \<
%%   Equals        \=     Greater than  \>     Question mark \?
%%   Commercial at \@     Left bracket  \[     Backslash     \\
%%   Right bracket \]     Circumflex    \^     Underscore    \_
%%   Grave accent  \`     Left brace    \{     Vertical bar  \|
%%   Right brace   \}     Tilde         \~}
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{timtm}
[2021/11/09 v1.0 Template for the Interactive Media Technology (TIMTM) and Media Management (TMMTM) programmes at KTH Royal Institute of Technology. ]
\def\@classname{timtm}
\InputIfFileExists{timtm-preload-hook.tex}{%
  \ClassWarning{\@classname}{%
    I am loading timtm-preload-hook.tex. You are fully responsible
    for any problems from now on.}}{}

%% If the thesis is in Swedish set the flag appropriately
\newif\ifinswedish
%\inswedishtrue

%% For enhanced digital output
\newif\ifdigitaloutput
\digitaloutputtrue

\RequirePackage{xkeyval}
\RequirePackage{xstring}
\RequirePackage{iftex}

% Make it possible to conditionally depend on the TeX-engine used
\newif\ifxeorlua
\ifxetex\xeorluatrue\fi
\ifluatex\xeorluatrue\fi



%% XeLaTeX and LuaTeX use UTF8 by default, otherwise set this to allow UTF8 input
\ifxeorlua \relax
\else
  \RequirePackage[utf8]{inputenc}
\fi

\define@choicekey*+{timtm.cls}{format}[\ACM@format\ACM@format@nr]{%
  manuscript, acmsmall, acmlarge, acmtog, sigconf}[manuscript]{}{%
  \ClassError{\@classname}{The option format must be manuscript,
    acmsmall, acmlarge, acmtog, sigconf}}
\def\@DeclareACMFormat#1{\DeclareOptionX{#1}{\setkeys{timtm.cls}{format=#1}}}
\@DeclareACMFormat{manuscript}
\@DeclareACMFormat{acmsmall}
\@DeclareACMFormat{acmlarge}
\@DeclareACMFormat{acmtog}
\@DeclareACMFormat{sigconf}
\ExecuteOptionsX{format}
\define@boolkey+{timtm.cls}[@ACM@]{screen}[true]{%
  \if@ACM@screen
    \PackageInfo{\@classname}{Using screen mode}%
  \else
    \PackageInfo{\@classname}{Not using screen mode}%
  \fi}{\PackageError{\@classname}{The option screen can be either true or
    false}}
\ExecuteOptionsX{screen=false}
\define@boolkey+{timtm.cls}[@ACM@]{urlbreakonhyphens}[true]{%
  \if@ACM@urlbreakonhyphens
    \PackageInfo{\@classname}{Using breaking urls on hyphens}%
  \else
    \PackageInfo{\@classname}{Not breaking urls on hyphens}%
  \fi}{\PackageError{\@classname}{The option urlbreakonhyphens can be either true or
    false}}
\ExecuteOptionsX{urlbreakonhyphens=true}
\define@boolkey+{timtm.cls}[@ACM@]{acmthm}[true]{%
  \if@ACM@acmthm
    \PackageInfo{\@classname}{Requiring acmthm}%
  \else
    \PackageInfo{\@classname}{Suppressing acmthm}%
  \fi}{\PackageError{\@classname}{The option acmthm can be either true or
    false}}
\ExecuteOptionsX{acmthm=true}
\define@boolkey+{timtm.cls}[@ACM@]{review}[true]{%
  \if@ACM@review
    \PackageInfo{\@classname}{Using review mode}%
    \AtBeginDocument{\@ACM@printfoliostrue}%
  \else
    \PackageInfo{\@classname}{Not using review mode}%
  \fi}{\PackageError{\@classname}{The option review can be either true or
    false}}
\ExecuteOptionsX{review=false}
%% removed authorversion option
\define@boolkey+{timtm.cls}[@ACM@]{balance}[true]{}{%
  \PackageError{\@classname}{The option balance can be either true or
    false}}
\ExecuteOptionsX{balance}
\define@boolkey+{timtm.cls}[@ACM@]{pbalance}[true]{}{%
  \PackageError{\@classname}{The option pbalance can be either true or
    false}}
\ExecuteOptionsX{pbalance=false}
\define@boolkey+{timtm.cls}[@ACM@]{natbib}[true]{%
  \if@ACM@natbib
    \PackageInfo{\@classname}{Explicitly selecting natbib mode}%
  \else
    \PackageInfo{\@classname}{Explicitly deselecting natbib mode}%
  \fi}{\PackageError{\@classname}{The option natbib can be either true or
    false}}
\ExecuteOptionsX{natbib=true}
%% Removed anonymous option
\define@boolkey+{timtm.cls}[@ACM@]{authordraft}[true]{%
  \if@ACM@authordraft
    \PackageInfo{\@classname}{Using authordraft mode}%
    \@ACM@reviewtrue
  \else
    \PackageInfo{\@classname}{Not using authordraft mode}%
  \fi}{\PackageError{\@classname}{The option authordraft can be either true or
    false}}
\ExecuteOptionsX{authordraft=false}
\def\ACM@fontsize{}
\DeclareOptionX{9pt}{\edef\ACM@fontsize{\CurrentOption}}
\DeclareOptionX{10pt}{\edef\ACM@fontsize{\CurrentOption}}
\DeclareOptionX{11pt}{\edef\ACM@fontsize{\CurrentOption}}
\DeclareOptionX{12pt}{\edef\ACM@fontsize{\CurrentOption}}
\DeclareOptionX{draft}{\PassOptionsToClass{\CurrentOption}{amsart}}
\DeclareOptionX{*}{\PassOptionsToClass{\CurrentOption}{amsart}}
\ProcessOptionsX
\ClassInfo{\@classname}{Using format \ACM@format, number \ACM@format@nr}

\ifx\ACM@fontsize\@empty
\def\ACM@fontsize{9pt}%
\fi
\ClassInfo{\@classname}{Using fontsize \ACM@fontsize}
\LoadClass[\ACM@fontsize, reqno]{amsart}
\RequirePackage{microtype}
\RequirePackage{etoolbox}
\RequirePackage{booktabs}
\RequirePackage{refcount}
\RequirePackage{totpages}
\RequirePackage{environ}

\RequirePackage{setspace}
\onehalfspacing

\RequirePackage{textcase}
\if@ACM@natbib
  \RequirePackage{natbib}
  \renewcommand{\bibsection}{%
     \section*{\refname}%
     \phantomsection\addcontentsline{toc}{section}{\refname}%
  }
  \renewcommand{\bibfont}{\bibliofont}
  \renewcommand\setcitestyle[1]{
  \@for\@tempa:=#1\do
  {\def\@tempb{round}\ifx\@tempa\@tempb
     \renewcommand\NAT@open{(}\renewcommand\NAT@close{)}\fi
   \def\@tempb{square}\ifx\@tempa\@tempb
     \renewcommand\NAT@open{[}\renewcommand\NAT@close{]}\fi
   \def\@tempb{angle}\ifx\@tempa\@tempb
     \renewcommand\NAT@open{$<$}\renewcommand\NAT@close{$>$}\fi
   \def\@tempb{curly}\ifx\@tempa\@tempb
     \renewcommand\NAT@open{\{}\renewcommand\NAT@close{\}}\fi
   \def\@tempb{semicolon}\ifx\@tempa\@tempb
     \renewcommand\NAT@sep{;}\fi
   \def\@tempb{colon}\ifx\@tempa\@tempb
     \renewcommand\NAT@sep{;}\fi
   \def\@tempb{comma}\ifx\@tempa\@tempb
     \renewcommand\NAT@sep{,}\fi
   \def\@tempb{authoryear}\ifx\@tempa\@tempb
     \NAT@numbersfalse\fi
   \def\@tempb{numbers}\ifx\@tempa\@tempb
     \NAT@numberstrue\NAT@superfalse\fi
   \def\@tempb{super}\ifx\@tempa\@tempb
     \NAT@numberstrue\NAT@supertrue\fi
   \def\@tempb{nobibstyle}\ifx\@tempa\@tempb
     \let\bibstyle=\@gobble\fi
   \def\@tempb{bibstyle}\ifx\@tempa\@tempb
     \let\bibstyle=\@citestyle\fi
   \def\@tempb{sort}\ifx\@tempa\@tempb
     \def\NAT@sort{\@ne}\fi
   \def\@tempb{nosort}\ifx\@tempa\@tempb
     \def\NAT@sort{\z@}\fi
   \def\@tempb{compress}\ifx\@tempa\@tempb
     \def\NAT@cmprs{\@ne}\fi
   \def\@tempb{nocompress}\ifx\@tempa\@tempb
     \def\NAT@cmprs{\z@}\fi
   \def\@tempb{sort&compress}\ifx\@tempa\@tempb
     \def\NAT@sort{\@ne}\def\NAT@cmprs{\@ne}\fi
   \def\@tempb{mcite}\ifx\@tempa\@tempb
     \let\NAT@merge\@ne\fi
   \def\@tempb{merge}\ifx\@tempa\@tempb
     \@ifnum{\NAT@merge<\tw@}{\let\NAT@merge\tw@}{}\fi
   \def\@tempb{elide}\ifx\@tempa\@tempb
     \@ifnum{\NAT@merge<\thr@@}{\let\NAT@merge\thr@@}{}\fi
   \def\@tempb{longnamesfirst}\ifx\@tempa\@tempb
     \NAT@longnamestrue\fi
   \def\@tempb{nonamebreak}\ifx\@tempa\@tempb
     \def\NAT@nmfmt#1{\mbox{\NAT@up#1}}\fi
   \expandafter\NAT@find@eq\@tempa=\relax\@nil
   \if\@tempc\relax\else
     \expandafter\NAT@rem@eq\@tempc
     \def\@tempb{open}\ifx\@tempa\@tempb
      \xdef\NAT@open{\@tempc}\fi
     \def\@tempb{close}\ifx\@tempa\@tempb
      \xdef\NAT@close{\@tempc}\fi
     \def\@tempb{aysep}\ifx\@tempa\@tempb
      \xdef\NAT@aysep{\@tempc}\fi
     \def\@tempb{yysep}\ifx\@tempa\@tempb
      \xdef\NAT@yrsep{\@tempc}\fi
     \def\@tempb{notesep}\ifx\@tempa\@tempb
      \xdef\NAT@cmt{\@tempc}\fi
     \def\@tempb{citesep}\ifx\@tempa\@tempb
      \xdef\NAT@sep{\@tempc}\fi
   \fi
  }%
  \NAT@@setcites
  }
  \renewcommand\citestyle[1]{%
    \ifcsname bibstyle@#1\endcsname%
    \csname bibstyle@#1\endcsname\let\bibstyle\@gobble%
    \else%
    \@latex@error{Undefined `#1' citestyle}%
    \fi
  }%
\fi
\newcommand{\bibstyle@acmauthoryear}{%
  \setcitestyle{%
    authoryear,%
    open={[},close={]},citesep={;},%
    aysep={},yysep={,},%
    notesep={, }}}
\newcommand{\bibstyle@acmnumeric}{%
  \setcitestyle{%
    numbers,sort&compress,%
    open={[},close={]},citesep={,},%
    notesep={, }}}
\if@ACM@natbib
\citestyle{acmnumeric}
\fi
\def\@startsection#1#2#3#4#5#6{%
  \if@noskipsec \leavevmode \fi
  \par
  \@tempskipa #4\relax
  \@afterindenttrue
  \ifdim \@tempskipa <\z@
    \@tempskipa -\@tempskipa \@afterindentfalse
  \fi
  \if@nobreak
    \everypar{}%
  \else
    \addpenalty\@secpenalty\addvspace\@tempskipa
  \fi
  \@ifstar
    {\@ssect{#3}{#4}{#5}{#6}}%
    {\@dblarg{\@sect{#1}{#2}{#3}{#4}{#5}{#6}}}}
\def\@sect#1#2#3#4#5#6[#7]#8{%
  \edef\@toclevel{\ifnum#2=\@m 0\else\number#2\fi}%
  \ifnum #2>\c@secnumdepth
    \let\@svsec\@empty
  \else
    \refstepcounter{#1}%
    \protected@edef\@svsec{\@seccntformat{#1}\relax}%
  \fi
  \@tempskipa #5\relax
  \ifdim \@tempskipa>\z@
    \begingroup
      #6{%
        \@hangfrom{\hskip #3\relax\@svsec}%
          \interlinepenalty \@M #8\@@par}%
    \endgroup
    \csname #1mark\endcsname{#7}%
    \ifnum #2>\c@secnumdepth \else
        \@tochangmeasure{\csname the#1\endcsname}%
    \fi
    \addcontentsline{toc}{#1}{%
      \ifnum #2>\c@secnumdepth \else
        \protect\numberline{\csname the#1\endcsname}%
      \fi
      #7}%
  \else
    \def\@svsechd{%
      #6{\hskip #3\relax
      \@svsec #8}%
      \csname #1mark\endcsname{#7}%
      \ifnum #2>\c@secnumdepth \else
        \@tochangmeasure{\csname the#1\endcsname\space}%
      \fi
      \addcontentsline{toc}{#1}{%
        \ifnum #2>\c@secnumdepth \else
          \protect\numberline{\csname the#1\endcsname}%
        \fi
        #7}}%
  \fi
  \@xsect{#5}}
\def\@xsect#1{%
  \@tempskipa #1\relax
  \ifdim \@tempskipa>\z@
    \par \nobreak
    \vskip \@tempskipa
    \@afterheading
  \else
    \@nobreakfalse
    \global\@noskipsectrue
    \everypar{%
      \if@noskipsec
        \global\@noskipsecfalse
       {\setbox\z@\lastbox}%
        \clubpenalty\@M
        \begingroup \@svsechd \endgroup
        \unskip
        \@tempskipa #1\relax
        \hskip -\@tempskipa
      \else
        \clubpenalty \@clubpenalty
        \everypar{}%
      \fi}%
  \fi
  \ignorespaces}
\def\@seccntformat#1{\csname the#1\endcsname\quad}
\def\@ssect#1#2#3#4#5{%
  \@tempskipa #3\relax
  \ifdim \@tempskipa>\z@
    \begingroup
      #4{%
        \@hangfrom{\hskip #1}%
          \interlinepenalty \@M #5\@@par}%
    \endgroup
  \else
    \def\@svsechd{#4{\hskip #1\relax #5}}%
  \fi
  \@xsect{#3}}
\def\@starttoc#1#2{\begingroup\makeatletter
  \setTrue{#1}%
  \par\removelastskip\vskip\z@skip
  \@startsection{section}\@M\z@{\linespacing\@plus\linespacing}%
    {.5\linespacing}{\centering\contentsnamefont}{#2}%
  \@input{\jobname.#1}%
  \if@filesw
    \@xp\newwrite\csname tf@#1\endcsname
    \immediate\@xp\openout\csname tf@#1\endcsname \jobname.#1\relax
  \fi
  \global\@nobreakfalse \endgroup
  \addvspace{32\p@\@plus14\p@}%
}
\def\l@section{\@tocline{1}{0pt}{1pc}{2pc}{}}
\def\l@subsection{\@tocline{2}{0pt}{1pc}{3pc}{}}
\def\l@subsubsection{\@tocline{3}{0pt}{1pc}{5pc}{}}
\def\@makefntext{\noindent\@makefnmark}
\long\def\@mpfootnotetext#1{%
  \global\setbox\@mpfootins\vbox{%
    \unvbox\@mpfootins
    \reset@font\footnotesize
    \hsize\columnwidth
    \@parboxrestore
    \protected@edef\@currentlabel
         {\csname p@mpfootnote\endcsname\@thefnmark}%
    \color@begingroup\centering
      \@makefntext{%
        \rule\z@\footnotesep\ignorespaces#1\@finalstrut\strutbox}%
    \color@endgroup}}
\def\@makefnmark{\hbox{\@textsuperscript{\normalfont\@thefnmark}}}
\RequirePackage{hyperxmp}
\let\@footnotemark@nolink\@footnotemark
\let\@footnotetext@nolink\@footnotetext
\RequirePackage[bookmarksnumbered,unicode]{hyperref}
\pdfstringdefDisableCommands{%
  \def\addtocounter#1#2{}%
  \def\unskip{}%
  \def\textbullet{- }%
  \def\textrightarrow{ -> }%
  \def\footnotemark{}%
}
\urlstyle{rm}
\ifcase\ACM@format@nr
\relax % manuscript
\or % acmsmall
\or % acmlarge
\or % acmtog
\or % sigconf
\or % siggraph
\or % sigplan
  \urlstyle{sf}
\fi
\AtEndPreamble{%
  \if@ACM@urlbreakonhyphens
    \def\do@url@hyp{\do\-}%
  \fi
  \if@ACM@screen
    \hypersetup{colorlinks,
      linkcolor=ACMPurple,
      citecolor=ACMPurple,
      urlcolor=ACMDarkBlue,
      filecolor=ACMDarkBlue}
    \else
    \hypersetup{hidelinks}
  \fi
  \hypersetup{pdflang={en},
    pdfdisplaydoctitle}}
\if@ACM@natbib
  \let\citeN\cite
  \let\cite\citep
  \let\citeANP\citeauthor
  \let\citeNN\citeyearpar
  \let\citeyearNP\citeyear
  \let\citeNP\citealt
  \DeclareRobustCommand\citeA
     {\begingroup\NAT@swafalse
       \let\NAT@ctype\@ne\NAT@partrue\NAT@fullfalse\NAT@open\NAT@citetp}%
  \providecommand\newblock{}%
\else
  \AtBeginDocument{%
    \let\shortcite\cite%
    \providecommand\citename[1]{#1}}
\fi
\newcommand\shortcite[2][]{%
  \ifNAT@numbers\cite[#1]{#2}\else\citeyearpar[#1]{#2}\fi}
\def\bibliographystyle#1{%
  \ifx\@begindocumenthook\@undefined\else
    \expandafter\AtBeginDocument
  \fi
    {\if@filesw
       \immediate\write\@auxout{\string\bibstyle{#1}}%
     \fi}}
\RequirePackage{graphicx}
\RequirePackage[prologue]{xcolor}
\definecolor[named]{ACMBlue}{cmyk}{1,0.1,0,0.1}
\definecolor[named]{ACMYellow}{cmyk}{0,0.16,1,0}
\definecolor[named]{ACMOrange}{cmyk}{0,0.42,1,0.01}
\definecolor[named]{ACMRed}{cmyk}{0,0.90,0.86,0}
\definecolor[named]{ACMLightBlue}{cmyk}{0.49,0.01,0,0}
\definecolor[named]{ACMGreen}{cmyk}{0.20,0,1,0.19}
\definecolor[named]{ACMPurple}{cmyk}{0.55,1,0,0.15}
\definecolor[named]{ACMDarkBlue}{cmyk}{1,0.58,0,0.21}
\if@ACM@authordraft
  \RequirePackage{draftwatermark}
  \SetWatermarkFontSize{0.5in}
  \SetWatermarkColor[gray]{.9}
  \SetWatermarkText{\parbox{12em}{\centering
      Unpublished working draft.\\
      Not for distribution.}}
\fi
\RequirePackage[a4paper,twoside,
  top=37mm,bottom=50mm,inner=45mm,outer=35mm,
  headsep=15mm,headheight=6mm,footskip=25mm]{geometry} % Set paper and contents dimensions

\setlength\parindent{10\p@}
\setlength\parskip{\z@}

\setlength\normalparindent{\parindent}
\def\copyrightpermissionfootnoterule{\kern-3\p@
  \hrule \@width \columnwidth \kern 2.6\p@}
\RequirePackage{manyfoot}
\SelectFootnoteRule[2]{copyrightpermission}
\DeclareNewFootnote{authorsaddresses}
\SelectFootnoteRule[2]{copyrightpermission}
\DeclareNewFootnote{copyrightpermission}
\def\footnoterule{\kern-3\p@
  \hrule \@width 4pc \kern 2.6\p@}
\def\endminipage{%
    \par
    \unskip
    \ifvoid\@mpfootins\else
      \vskip\skip\@mpfootins
      \normalcolor
      \unvbox\@mpfootins
    \fi
    \@minipagefalse
  \color@endgroup
  \egroup
  \expandafter\@iiiparbox\@mpargs{\unvbox\@tempboxa}}
\def\@textbottom{\vskip \z@ \@plus 1pt}
\let\@texttop\relax
\ifcase\ACM@format@nr
\relax % manuscript
  \flushbottom
\or % sigconf
  \flushbottom
\fi
\ifPDFTeX
\input{glyphtounicode}              %% The following are for ligatures
\pdfglyphtounicode{f_f}{FB00}
\pdfglyphtounicode{f_f_i}{FB03}
\pdfglyphtounicode{f_f_l}{FB04}
\pdfglyphtounicode{f_i}{FB01}
\pdfglyphtounicode{t_t}{0074 0074}
\pdfglyphtounicode{f_t}{0066 0074}
\pdfglyphtounicode{T_h}{0054 0068}
\pdfgentounicode=1
\RequirePackage{cmap}
\fi

%% For degree project reports use Times, Cusor, etc. fonts
%% rather than the “Libertine” typeface family used by ACM's conference format
\ifxeorlua
  \RequirePackage{fontspec}
  \defaultfontfeatures{Ligatures={TeX}} % This enables TeX style ligatures such as ---, '', ``, and so on
  \setmainfont{TeX Gyre Termes}  %% Times like font
  \setsansfont{TeX Gyre Heros}   %% Helvetica like font
  \setmonofont{TeX Gyre Cursor}  %% Courier like font
\else
  \RequirePackage[T1]{fontenc}
  \RequirePackage{tgtermes}
  \RequirePackage{tgheros}
  \RequirePackage{tgcursor}
\fi

\let\liningnums\@undefined
\AtEndPreamble{%
  \DeclareTextFontCommand{\liningnums}{\libertineLF}}
\newif\if@Description@present
\@Description@presenttrue
\newif\if@undescribed@images
\@undescribed@imagesfalse
\newcommand\Description[2][]{\global\@Description@presenttrue\ignorespaces}
\AtEndDocument{\if@undescribed@images
  \ClassWarningNoLine{\@classname}{Some images may lack descriptions}\fi}
\AtBeginEnvironment{figure}{\@Description@presentfalse
  \let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{figure*}{\@Description@presentfalse
  \let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtEndEnvironment{figure}{\if@Description@present\else
  \global\@undescribed@imagestrue
  \ClassWarning{\@classname}{A possible image without description}\fi}
\AtEndEnvironment{figure*}{\if@Description@present\else
  \global\@undescribed@imagestrue
  \ClassWarning{\@classname}{A possible image without description}\fi}
\AtBeginEnvironment{table}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{table*}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{algorithm}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{algorithm*}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{lstlisting}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{lstlisting*}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{minted}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{minted*}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{listing}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}
\AtBeginEnvironment{listing*}{\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig}

\RequirePackage{caption, float}
\captionsetup[table]{position=top}

\captionsetup{labelfont={bf},
    textfont={bf}, labelsep=colon, margin=\z@}
  \ifcase\ACM@format@nr
  \relax % manuscript
  \or % acmsmall
  \or % acmlarge
  \or % acmtog
  \or % sigconf
  \or % siggraph
    \captionsetup{textfont={it}}
  \fi

\newfloat{sidebar}{}{sbar}
\floatname{sidebar}{Sidebar}
\renewenvironment{sidebar}{\Collect@Body\@sidebar}{}
\long\def\@sidebar#1{\bgroup\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig\captionsetup{type=sidebar}%
  \marginpar{\small#1}\egroup}
\newenvironment{marginfigure}{\Collect@Body\@marginfigure}{}
\long\def\@marginfigure#1{\bgroup
  \let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig
  \captionsetup{type=figure}%
  \marginpar{\@Description@presentfalse\centering
    \small#1\if@Description@present\else
      \global\@undescribed@imagestrue
      \ClassWarning{\@classname}{A possible image without description}
      \fi}%
  \egroup}
\newenvironment{margintable}{\Collect@Body\@margintable}{}
\long\def\@margintable#1{\bgroup\let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig\captionsetup{type=table}%
  \marginpar{\centering\small#1}\egroup}
\newdimen\fulltextwidth
\fulltextwidth=\dimexpr(\textwidth+\marginparwidth+\marginparsep)

\def\@endwidefloatbox{%
  \par\vskip\z@skip
  \@minipagefalse
  \outer@nobreak
  \egroup
  \color@endbox
  \global\setbox\@currbox=\vbox{\moveleft
    \dimexpr(\fulltextwidth-\textwidth)\box\@currbox}%
  \wd\@currbox=\textwidth
}
\ifcase\ACM@format@nr
\relax % manuscript
\or % acmsmall
\or % acmlarge
\or % acmtog
\or % sigconf
\or % siggraph
\or % sigplan
\def\labelenumi{\theenumi.}
\def\labelenumii{\theenumii.}
\def\labelenumiii{\theenumiii.}
\def\labelenumiv{\theenumiv.}
\fi
\newdimen\@ACM@labelwidth
\AtBeginDocument{%
  \setlength\labelsep{4pt}
  \setlength{\@ACM@labelwidth}{6.5pt}

  %% First-level list: when beginning after the first line of an
  %% indented paragraph or ending before an indented paragraph, labels
  %% should not hang to the left of the preceding/following text.
  \setlength\leftmargini{\z@}
  \addtolength\leftmargini{\parindent}
  \addtolength\leftmargini{2\labelsep}
  \addtolength\leftmargini{\@ACM@labelwidth}

  %% Second-level and higher lists.
  \setlength\leftmarginii{\z@}
  \addtolength\leftmarginii{0.5\labelsep}
  \addtolength\leftmarginii{\@ACM@labelwidth}
  \setlength\leftmarginiii{\leftmarginii}
  \setlength\leftmarginiv{\leftmarginiii}
  \setlength\leftmarginv{\leftmarginiv}
  \setlength\leftmarginvi{\leftmarginv}
  \@listi}
\newskip\listisep
\listisep\smallskipamount
\def\@listI{\leftmargin\leftmargini
  \labelwidth\leftmargini \advance\labelwidth-\labelsep
  \listparindent\z@
  \topsep\listisep}
\let\@listi\@listI
\def\@listii{\leftmargin\leftmarginii
  \labelwidth\leftmarginii \advance\labelwidth-\labelsep
  \topsep\z@skip}
\def\@listiii{\leftmargin\leftmarginiii
  \labelwidth\leftmarginiii \advance\labelwidth-\labelsep}
\def\@listiv{\leftmargin\leftmarginiv
  \labelwidth\leftmarginiv \advance\labelwidth-\labelsep}
\def\@listv{\leftmargin\leftmarginv
  \labelwidth\leftmarginv \advance\labelwidth-\labelsep}
\def\@listvi{\leftmargin\leftmarginvi
  \labelwidth\leftmarginvi \advance\labelwidth-\labelsep}
\renewcommand{\descriptionlabel}[1]{\upshape\bfseries #1}
\renewenvironment{description}{\list{}{%
    \labelwidth\@ACM@labelwidth
    \let\makelabel\descriptionlabel}%
}{
  \endlist
}
\let\enddescription=\endlist % for efficiency

\def\subtitle#1{\def\@subtitle{#1}}
\subtitle{}

%% Add alternative title and subtitle - to provide a Swedish language title and subtitle
\let\@alttitle\@empty
\newcommand{\alttitle}[1]{\def\@alttitle{#1}}
\let\@altsubtitle\@empty
\newcommand{\altsubtitle}[1]{\def\@altsubtitle{#1}}

\newcount\num@authorgroups
\num@authorgroups=0\relax
\newcount\num@authors
\num@authors=0\relax
\newif\if@insideauthorgroup
\@insideauthorgroupfalse
\renewcommand\author[2][]{%
  \IfSubStr{\detokenize{#2}}{,}{\ClassWarning{\@classname}{Do not put several
      authors in the same \string\author\space macro!}}{}%
  \global\advance\num@authors by 1\relax
  \if@insideauthorgroup\else
    \global\advance\num@authorgroups by 1\relax
    \global\@insideauthorgrouptrue
  \fi
  \ifx\addresses\@empty
      \expandafter\gdef\expandafter\addresses\expandafter{%
        \expandafter\@author\expandafter{%
          \csname typeset@author\the\num@authors\endcsname{#2}}}%
      \gdef\authors{#2}%
  \else
    \expandafter\g@addto@macro\expandafter\addresses\expandafter{%
      \expandafter\and\expandafter\@author\expandafter{%
        \csname typeset@author\the\num@authors\endcsname{#2}}}%
      \g@addto@macro\authors{\and#2}%
  \fi

    \def\@tempa{#1}%
    \ifx\@tempa\@empty
      \ifx\shortauthors\@empty
        \gdef\shortauthors{#2}%
      \else
        \g@addto@macro\shortauthors{\and#2}%
      \fi
    \else
      \ifx\shortauthors\@empty
        \gdef\shortauthors{#1}%
      \else
        \g@addto@macro\shortauthors{\and#1}%
      \fi
  \fi}
\newcommand{\affiliation}[2][]{%
  \global\@insideauthorgroupfalse
    \g@addto@macro\addresses{\affiliation{#1}{#2}}%
}
\define@boolkey+{@ACM@affiliation@}[@ACM@affiliation@]{obeypunctuation}%
[true]{}{\ClassError{\@classname}{The option obeypunctuation can be either true or false}}
\def\additionalaffiliation#1{\authornote{\@additionalaffiliation{#1}}}
\def\@additionalaffiliation#1{\bgroup
  \def\position##1{\ignorespaces}%
  \def\institution##1{##1\ignorespaces}%
  \def\department{\@ifnextchar[{\@department}{\@department[]}}%
  \def\@department[##1]##2{\unskip, ##2\ignorespaces}%
  \let\streetaddress\position
  \let\city\position
  \let\state\position
  \let\postcode\position
  \let\country\position
  Also with #1\unskip.\egroup}
\renewcommand{\email}[2][]{%
  \IfSubStr{#2}{,}{\ClassWarning{\@classname}{Do not put several
      addresses in the same \string\email\space macro!}}{}%
    \g@addto@macro\addresses{\email{#1}{#2}}%
}
\def\orcid#1{\unskip\ignorespaces%
  \IfBeginWith{#1}{http}{%
    \expandafter\gdef\csname
        typeset@author\the\num@authors\endcsname##1{%
          \href{#1}{##1}}}{%
    \expandafter\gdef\csname
        typeset@author\the\num@authors\endcsname##1{%
          \href{https://orcid.org/#1}{##1}}}}
\def\authorsaddresses#1{\def\@authorsaddresses{#1}}
\authorsaddresses{\@mkauthorsaddresses}
\def\@titlenotes{}
\def\titlenote#1{%
  \g@addto@macro\@title{\footnotemark}%
    \g@addto@macro\@titlenotes{\stepcounter{footnote}\footnotetext{#1}}%
}
\def\@subtitlenotes{}
\def\subtitlenote#1{%
  \g@addto@macro\@subtitle{\footnotemark}%
    \g@addto@macro\@subtitlenotes{%
      \stepcounter{footnote}\footnotetext{#1}}%
}
\def\@authornotes{}
\def\authornote#1{%
    \g@addto@macro\addresses{\@authornotemark}%
    \g@addto@macro\@authornotes{%
      \stepcounter{footnote}\footnotetext{#1}}%
 }
\newcommand\authornotemark[1][\relax]{%
  \ifx#1\relax\relax\relax
  \g@addto@macro\addresses{\@authornotemark}%
  \else
  \g@addto@macro\addresses{\@@authornotemark{#1}}%
  \fi}
\def\acmVolume#1{\def\@acmVolume{#1}}
\acmVolume{1}
\def\acmNumber#1{\def\@acmNumber{#1}}
\acmNumber{1}
\def\acmArticle#1{\def\@acmArticle{#1}}
\acmArticle{}
\def\acmArticleSeq#1{\def\@acmArticleSeq{#1}}
\acmArticleSeq{\@acmArticle}
\def\acmYear#1{\def\@acmYear{#1}}
\acmYear{\the\year}
\def\acmMonth#1{\def\@acmMonth{#1}}
\acmMonth{\the\month}
\def\@acmPubDate{\ifcase\@acmMonth\or
  January\or February\or March\or April\or May\or June\or
  July\or August\or September\or October\or November\or
  December\fi~\@acmYear}
\def\acmPrice#1{\def\@acmPrice{#1}}
\acmPrice{15.00}
\def\acmSubmissionID#1{\def\@acmSubmissionID{#1}}
\acmSubmissionID{}
\def\acmISBN#1{\def\@acmISBN{#1}}
\acmISBN{978-x-xxxx-xxxx-x/YY/MM}
\def\acmDOI#1{\def\@acmDOI{#1}}
\acmDOI{10.1145/nnnnnnn.nnnnnnn}
\newif\if@ACM@badge
\@ACM@badgefalse
\newlength\@ACM@badge@width
\setlength\@ACM@badge@width{5pc}
\newlength\@ACM@title@width
\newlength\@ACM@badge@skip
\setlength\@ACM@badge@skip{1pc}
\newcommand\acmBadgeR[2][]{\@ACM@badgetrue
  \def\@acmBadgeR@url{#1}%
  \def\@acmBadgeR@image{#2}}
\def\@acmBadgeR@url{}
\def\@acmBadgeR@image{}
\newcommand\acmBadgeL[2][]{\@ACM@badgetrue
  \def\@acmBadgeL@url{#1}%
  \def\@acmBadgeL@image{#2}}
\def\@acmBadgeL@url{}
\def\@acmBadgeL@image{}
\def\startPage#1{\def\@startPage{#1}}
\startPage{}
\def\terms#1{\ClassWarning{\@classname}{The command \string\terms{} is
    obsolete.  I am going to ignore it}}
\def\keywords#1{\def\@keywords{#1}}
\let\@keywords\@empty
\AtEndDocument{\ifx\@keywords\@empty
  \ifnum\getrefnumber{TotPages}>2\relax
  \ClassWarningNoLine{\@classname}{ACM keywords are mandatory
    for papers over two pages}%
  \fi\fi}
\let\@SwedishKeywords\@empty
\newcommand{\SwedishKeywords}[1]{\def\@SwedishKeywords{#1}}
\renewenvironment{abstract}{}{}
\newenvironment{swedishabstract}{}{}
\define@boolkey+{@ACM@topmatter@}[@ACM@]{printccs}[true]{%
  \if@ACM@printccs
    \ClassInfo{\@classname}{Printing CCS}%
  \else
    \ClassInfo{\@classname}{Suppressing CCS}%
  \fi}{\ClassError{\@classname}{The option printccs can be either true or false}}
\define@boolkey+{@ACM@topmatter@}[@ACM@]{printacmref}[true]{%
  \if@ACM@printacmref
    \ClassInfo{\@classname}{Printing bibformat}%
  \else
    \ClassInfo{\@classname}{Suppressing bibformat}%
  \fi}{\ClassError{\@classname}{The option printacmref can be either true or false}}
\define@boolkey+{@ACM@topmatter@}[@ACM@]{printfolios}[true]{%
  \if@ACM@printfolios
    \ClassInfo{\@classname}{Printing folios}%
  \else
    \ClassInfo{\@classname}{Suppressing folios}%
  \fi}{\ClassError{\@classname}{The option printfolios can be either true or false}}

\def\settopmatter#1{\setkeys{@ACM@topmatter@}{#1}}
\settopmatter{printccs=true, printacmref=true}

\settopmatter{printfolios=true}

\def\@received{}
\newcommand\received[2][]{\def\@tempa{#1}%
  \ifx\@tempa\@empty
    \ifx\@received\@empty
      \gdef\@received{Received #2}%
    \else
      \g@addto@macro{\@received}{; revised #2}%
    \fi
  \else
    \ifx\@received\@empty
      \gdef\@received{#1 #2}%
    \else
      \g@addto@macro{\@received}{; #1 #2}%
    \fi
  \fi}
\AtEndDocument{%
  \ifx\@received\@empty\else
    \par\bigskip\noindent\small\normalfont\@received\par
  \fi}
\RequirePackage{comment}
\excludecomment{CCSXML}
\let\@concepts\@empty
\newcounter{@concepts}
\newcommand\ccsdesc[2][100]{%
  \ccsdesc@parse#1~#2~~\ccsdesc@parse@end}
\def\textrightarrow{$\rightarrow$}
\def\ccsdesc@parse#1~#2~#3~{%
  \stepcounter{@concepts}%
  \expandafter\ifx\csname CCS@General@#2\endcsname\relax
    \expandafter\gdef\csname CCS@General@#2\endcsname{\textbullet\
      \textbf{#2}}%
    \expandafter\gdef\csname CCS@Punctuation@#2\endcsname{; }%
    \expandafter\gdef\csname CCS@Specific@#2\endcsname{}%
  \g@addto@macro{\@concepts}{\csname CCS@General@#2\endcsname
    \csname CCS@Punctuation@#2\endcsname
    \csname CCS@Specific@#2\endcsname}%
  \fi
  \ifx#3\relax\relax\else
    \expandafter\gdef\csname CCS@Punctuation@#2\endcsname{
      \textrightarrow\ }%
    \expandafter\g@addto@macro\expandafter{\csname CCS@Specific@#2\endcsname}{%
     \addtocounter{@concepts}{-1}%
     \ifnum#1>499\textbf{#3}\else
     \ifnum#1>299\textit{#3}\else
     #3\fi\fi\ifnum\value{@concepts}=0.\else; \fi}%
  \fi
\ccsdesc@parse@finish}
\def\ccsdesc@parse@finish#1\ccsdesc@parse@end{}
\newif\if@printcopyright
\@printcopyrighttrue
\newif\if@printpermission
\@printpermissiontrue
\newif\if@acmowned
\@acmownedtrue
\define@choicekey*{ACM@}{acmcopyrightmode}[%
  \acm@copyrightinput\acm@copyrightmode]{none,%
    acmcopyright,acmlicensed,rightsretained,%
    usgov,usgovmixed,cagov,cagovmixed,licensedusgovmixed,%
    licensedcagov,licensedcagovmixed,othergov,licensedothergov,%
    iw3c2w3,iw3c2w3g}{%
  \@printpermissiontrue
  \@printcopyrighttrue
  \@acmownedtrue
  \ifnum\acm@copyrightmode=0\relax % none
   \@printpermissionfalse
   \@printcopyrightfalse
   \@acmownedfalse
  \fi
  \ifnum\acm@copyrightmode=2\relax % acmlicensed
   \@acmownedfalse
  \fi
  \ifnum\acm@copyrightmode=3\relax % rightsretained
   \@acmownedfalse
   \@printpermissionfalse                   %% No need for this for a thesis - as it will be an offentlig avhandling
   \AtBeginDocument{\acmPrice{}}%
  \fi
  \ifnum\acm@copyrightmode=4\relax % usgov
   \@printpermissiontrue
   \@printcopyrightfalse
   \@acmownedfalse
   \AtBeginDocument{\acmPrice{}}%
  \fi
  \ifnum\acm@copyrightmode=6\relax % cagov
   \@acmownedfalse
  \fi
  \ifnum\acm@copyrightmode=8\relax % licensedusgovmixed
   \@acmownedfalse
  \fi
  \ifnum\acm@copyrightmode=9\relax % licensedcagov
   \@acmownedfalse
  \fi
  \ifnum\acm@copyrightmode=10\relax % licensedcagovmixed
   \@acmownedfalse
  \fi
  \ifnum\acm@copyrightmode=11\relax % othergov
   \@acmownedtrue
  \fi
  \ifnum\acm@copyrightmode=12\relax % licensedothergov
   \@acmownedfalse
  \fi
  \ifnum\acm@copyrightmode=13\relax % iw3c2w3
   \@acmownedfalse
   \AtBeginDocument{\acmPrice{}}%
  \fi
  \ifnum\acm@copyrightmode=14\relax % iw3c2w3g
   \@acmownedfalse
   \AtBeginDocument{\acmPrice{}}%
  \fi}
\def\setcopyright#1{\setkeys{ACM@}{acmcopyrightmode=#1}}
\setcopyright{acmcopyright}
\def\@copyrightowner{%
  \ifcase\acm@copyrightmode\relax % none
  \or % acmcopyright
  Association for Computing Machinery.
  \or % acmlicensed
  Copyright held by the owner/author(s). Publication rights licensed to
  ACM\@.
  \or % rightsretained
  Copyright held by the \ifnum\num@authors>1\relax
  authors\else author\fi.
  \or % usgov
  \or % usgovmixed
  Association for Computing Machinery.
  \or % cagov
  Crown in Right of Canada.
  \or %cagovmixed
  Association for Computing Machinery.
  \or %licensedusgovmixed
  Copyright held by the owner/author(s). Publication rights licensed to
  ACM\@.
  \or % licensedcagov
  Crown in Right of Canada. Publication rights licensed to
  ACM\@.
  \or %licensedcagovmixed
  Copyright held by the owner/author(s). Publication rights licensed to
  ACM\@.
  \or % othergov
  Association for Computing Machinery.
  \or % licensedothergov
  Copyright held by the owner/author(s). Publication rights licensed to
  ACM\@.
  \or % ic2w3www
  IW3C2 (International World Wide Web Conference Committee), published
  under Creative Commons CC-BY~4.0 License.
  \or % ic2w3wwwgoogle
  IW3C2 (International World Wide Web Conference Committee), published
  under Creative Commons CC-BY-NC-ND~4.0 License.
  \fi}
\def\@formatdoi#1{\url{https://doi.org/#1}}
\def\@copyrightpermission{%
  \ifcase\acm@copyrightmode\relax % none
  \or % acmcopyright
   Permission to make digital or hard copies of all or part of this
   work for personal or classroom use is granted without fee provided
   that copies are not made or distributed for profit or commercial
   advantage and that copies bear this notice and the full citation on
   the first page. Copyrights for components of this work owned by
   others than ACM must be honored. Abstracting with credit is
   permitted. To copy otherwise, or republish, to post on servers or to
   redistribute to lists, requires prior specific permission
   and\hspace*{.5pt}/or  a fee. Request permissions from
   permissions@acm.org.
  \or % acmlicensed
   Permission to make digital or hard copies of all or part of this
   work for personal or classroom use is granted without fee provided
   that copies are not made or distributed for profit or commercial
   advantage and that copies bear this notice and the full citation on
   the first page. Copyrights for components of this work owned by
   others than the author(s) must be honored. Abstracting with credit
   is permitted.  To copy otherwise, or republish, to post on servers
   or to  redistribute to lists, requires prior specific permission
   and\hspace*{.5pt}/or  a fee. Request permissions from
   permissions@acm.org.
  \or % rightsretained
   Permission to make digital or hard copies of part or all of this work
   for personal or classroom use is granted without fee provided that
   copies are not made or distributed for profit or commercial advantage
   and that copies bear this notice and the full citation on the first
   page. Copyrights for third-party components of this work must be
   honored. For all other uses, contact the
   \ifnum\num@authors>1\relax
  authors\else author\fi.
  \or % usgov
   This paper is authored by an employee(s) of the United States
   Government and is in the public domain. Non-exclusive copying or
   redistribution is allowed, provided that the article citation is
   given and the authors and agency are clearly identified as its
   source.
  \or % usgovmixed
   ACM acknowledges that this contribution was authored or co-authored
   by an employee, contractor, or affiliate of the United States
   government. As such, the United States government retains a
   nonexclusive, royalty-free right to publish or reproduce this
   article, or to allow others to do so, for government purposes only.
  \or % cagov
   This article was authored by employees of the Government of Canada.
   As such, the Canadian government retains all interest in the
   copyright to this work and grants to ACM a nonexclusive,
   royalty-free right to publish or reproduce this article, or to allow
   others to do so, provided that clear attribution is given both to
   the authors and the Canadian government agency employing them.
   Permission to make digital or hard copies for personal or classroom
   use is granted. Copies must bear this notice and the full citation
   on the first page.  Copyrights for components of this work owned by
   others than the Canadian Government must be honored. To copy
   otherwise, distribute, republish, or post, requires prior specific
   permission and\hspace*{.5pt}/or a fee. Request permissions from
   permissions@acm.org.
  \or % cagovmixed
   ACM acknowledges that this contribution was co-authored by an
   affiliate of the national government of Canada. As such, the Crown
   in Right of Canada retains an equal interest in the copyright.
   Reprints must include clear attribution to ACM and the author's
   government agency affiliation.  Permission to make digital or hard
   copies for personal or classroom use is granted.  Copies must bear
   this notice and the full citation on the first page. Copyrights for
   components of this work owned by others than ACM must be honored.
   To copy otherwise, distribute, republish, or post, requires prior
   specific permission and\hspace*{.5pt}/or a fee. Request permissions
   from permissions@acm.org.
  \or % licensedusgovmixed
   Publication rights licensed to ACM\@. ACM acknowledges that this
   contribution was authored or co-authored by an employee, contractor
   or affiliate of the United States government. As such, the
   Government retains a nonexclusive, royalty-free right to publish or
   reproduce this article, or to allow others to do so, for Government
   purposes only.
  \or % licensedcagov
   This article was authored by employees of the Government of Canada.
   As such, the Canadian government retains all interest in the
   copyright to this work and grants to ACM a nonexclusive,
   royalty-free right to publish or reproduce this article, or to allow
   others to do so, provided that clear attribution is given both to
   the authors and the Canadian government agency employing them.
   Permission to make digital or hard copies for personal or classroom
   use is granted. Copies must bear this notice and the full citation
   on the first page.  Copyrights for components of this work owned by
   others than the Canadian Government must be honored. To copy
   otherwise, distribute, republish, or post, requires prior specific
   permission and\hspace*{.5pt}/or a fee. Request permissions from
   permissions@acm.org.
  \or % licensedcagovmixed
   Publication rights licensed to ACM\@. ACM acknowledges that this
   contribution was authored or co-authored by an employee, contractor
   or affiliate of the national government of Canada. As such, the
   Government retains a nonexclusive, royalty-free right to publish or
   reproduce this article, or to allow others to do so, for Government
   purposes only.
  \or % othergov
   ACM acknowledges that this contribution was authored or co-authored
   by an employee, contractor or affiliate of a national government. As
   such, the Government retains a nonexclusive, royalty-free right to
   publish or reproduce this article, or to allow others to do so, for
   Government purposes only.
  \or % licensedothergov
   Publication rights licensed to ACM\@. ACM acknowledges that this
   contribution was authored or co-authored by an employee, contractor
   or affiliate of a national government. As such, the Government
   retains a nonexclusive, royalty-free right to publish or reproduce
   this article, or to allow others to do so, for Government purposes
   only.
 \or % iw3c2w3
   This paper is published under the Creative Commons Attribution~4.0
   International (CC-BY~4.0) license. Authors reserve their rights to
   disseminate the work on their personal and corporate Web sites with
   the appropriate attribution.
 \or % iw3c2w3g
   This paper is published under the Creative Commons
   Attribution-NonCommercial-NoDerivs~4.0 International
   (CC-BY-NC-ND~4.0) license. Authors reserve their rights to
   disseminate the work on their personal and corporate Web sites with
   the appropriate attribution.
 \fi}
\def\copyrightyear#1{\def\@copyrightyear{#1}}
\copyrightyear{\@acmYear}

%% Ignore teaserfighures
\newenvironment{teaserfigure}{}{}

\renewcommand{\thanks}[1]{%
  \@ifnotempty{#1}{%
    \g@addto@macro\thankses{\thanks{#1}}%
   \fi}}
\ifx\@beginmaketitlehook\@undefined
  \let\@beginmaketitlehook\@empty
\fi
\def\AtBeginMaketitle{\g@addto@macro\@beginmaketitlehook}
\newbox\mktitle@bx
\def\maketitle{\@beginmaketitlehook
  \begingroup
  \let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig
  \let\@footnotemark\@footnotemark@nolink
  \let\@footnotetext\@footnotetext@nolink
  \renewcommand\thefootnote{\@fnsymbol\c@footnote}%
  \hsize=\textwidth
  \def\@makefnmark{\hbox{\@textsuperscript{\@thefnmark}}}%
  \@mktitle \@mkauthors
  \@printtopmatter
  \setcounter{footnote}{0}%
  \def\@makefnmark{\hbox{\@textsuperscript{\normalfont\@thefnmark}}}%
  \@titlenotes
  \@subtitlenotes
  \@authornotes
  \let\@makefnmark\relax
  \let\@thefnmark\relax
  \let\@makefntext\noindent
  \ifx\@empty\thankses\else
    \footnotetextauthorsaddresses{%
      \def\par{\let\par\@par}\parindent\z@\@setthanks}%
  \fi
  \ifx\@empty\@authorsaddresses\else
         \footnotetextauthorsaddresses{%
           \def\par{\let\par\@par}\parindent\z@\@setauthorsaddresses}%
  \fi
  \footnotetextcopyrightpermission{%
    \parindent\z@\parskip0.1\baselineskip
    \if@printpermission\@copyrightpermission\par\fi
    Document date: \today\par
   \ifx\@alttitle\empty\relax\else Swedish title: \@alttitle\par \fi
    \ifx\@altsubtitle\@empty\relax \else Swedish subtitle: \@altsubtitle\par \fi
    \if@printcopyright
      \copyright\ \@copyrightyear\ \@copyrightowner\\
    \else
      \@copyrightyear.\
    \fi
  }
  \endgroup
  \setcounter{footnote}{0}%
  \@mkabstract
  \@mkswedishabstract
  \if@ACM@printccs
  \ifx\@concepts\@empty\else\bgroup
      {\@specialsection{CCS Concepts}%
         \noindent\@concepts\par}\egroup
     \fi
   \fi
   \ifx\@keywords\@empty\else\bgroup
      {
         \@specialsection{Keywords}%
         \noindent\@keywords\par}\egroup
   \fi
   \ifx\@SwedishKeywords\@empty\else\bgroup
      {\@specialsection{Nyckelord}%
       \noindent\@SwedishKeywords\par}\egroup
   \fi
  \let\metadata@authors=\authors
  \nxandlist{, }{, }{, }\metadata@authors
  \def\@ACM@checkaffil{}%
  \hypersetup{%
    pdfauthor={\metadata@authors},
    pdftitle={\@title},
    pdfsubject={\@concepts},
    pdfkeywords={\@keywords},
    pdfcreator={LaTeX with acmart
      \csname ver@timtm.cls\endcsname\space
      and hyperref
      \csname ver@hyperref.sty\endcsname}}%
  \andify\authors
  \andify\shortauthors
  \global\let\authors=\authors
  \global\let\shortauthors=\shortauthors
  \if@ACM@printacmref
     \@mkbibcitation
  \fi
  \global\@topnum\z@ % this prevents floats from falling
                     % at the top of page 1
  \global\@botnum\z@ % we do not want them to be on the bottom either
  \@printendtopmatter
  \@afterindentfalse
  \@afterheading
}
\def\@specialsection#1{%
  \let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig
  \ifcase\ACM@format@nr
  \relax % manuscript
    \par\medskip\small\noindent#1: %
  \or % acmsmall
    \par\medskip\small\noindent#1: %
  \or % acmlarge
    \par\medskip\small\noindent#1: %
  \or % acmtog
    \par\medskip\small\noindent#1: %
  \or % sigconf
    \section*{#1}%
    \fi
  \let\@vspace\@vspace@acm
  \let\@vspacer\@vspacer@acm
}
\def\@printtopmatter{%
  \ifx\@startPage\@empty
     \gdef\@startPage{1}%
  \else
     \setcounter{page}{\@startPage}%
  \fi
  \@tempdima=\ht\mktitle@bx
  \advance\@tempdima by \dp\mktitle@bx
  \ifdim\@tempdima>0.9\textheight
    \loop
      \setbox\@tempboxa=\vsplit \mktitle@bx to 0.9\textheight
      \thispagestyle{firstpagestyle}%
      \noindent\unvbox\@tempboxa
      \clearpage
      \@tempdima=\ht\mktitle@bx
      \advance\@tempdima by \dp\mktitle@bx
    \ifdim\@tempdima>0.9\textheight\repeat
  \fi
  \thispagestyle{firstpagestyle}%
  \noindent
  \ifcase\ACM@format@nr
  \relax % manuscript
    \box\mktitle@bx\par
  \or % acmsmall
    \box\mktitle@bx\par
  \or % acmlarge
    \box\mktitle@bx\par
  \or % acmtog
    \twocolumn[\box\mktitle@bx]%
  \or % sigconf
    \twocolumn[\box\mktitle@bx]%
  \fi
}
\def\@mktitle{%
    \@mktitle@i
}
\def\@titlefont{%
% manuscript
    \LARGE\sffamily\bfseries
}
\def\@subtitlefont{\normalsize
% manuscript
    \mdseries
}
\def\@mktitle@i{\hsize=\textwidth
  \@ACM@title@width=\hsize

  \setbox\mktitle@bx=\vbox{\noindent\@titlefont
    \parbox[t]{\@ACM@title@width}{\raggedright
      \@titlefont\noindent
      \@title
  \ifx\@subtitle\@empty\else
    \par\noindent{\@subtitlefont\@subtitle}
  \fi}%
  \par\bigskip}}%

\newbox\@ACM@commabox
\def\@ACM@addtoaddress#1{%
  \ifvmode\else
    \if@ACM@affiliation@obeypunctuation\else
    \setbox\@ACM@commabox=\hbox{, }%
    \unskip\cleaders\copy\@ACM@commabox\hskip\wd\@ACM@commabox
  \fi\fi
  #1}
\def\streetaddress#1{\unskip\ignorespaces}
\def\postcode#1{\unskip\ignorespaces}

  \def\position#1{\if@ACM@affiliation@obeypunctuation#1\else#1\par\fi}%
  \def\institution#1{\global\@ACM@instpresenttrue
    \if@ACM@affiliation@obeypunctuation#1\else#1\par\fi}%
  \newcommand\department[2][0]{\if@ACM@affiliation@obeypunctuation
    #2\else#2\par\fi}%
  \def\city#1{\global\@ACM@citypresenttrue\@ACM@addtoaddress{#1}}%
  \let\state\@ACM@addtoaddress
  \def\country#1{\global\@ACM@countrypresenttrue\@ACM@addtoaddress{#1}}%

\def\@mkauthors{\begingroup
  \hsize=\textwidth
    \@mkauthors@i
  \endgroup
}
\def\@authorfont{\Large\sffamily}
\def\@affiliationfont{\normalsize\normalfont}

\def\@typeset@author@line{%
  \andify\@currentauthors\par\noindent
  \@currentauthors\def\@currentauthors{}%
% There is no reason to list an affiliation for the authors here.  
%  \ifx\@currentaffiliations\@empty\else
%    \andify\@currentaffiliations
%      \unskip, {\@currentaffiliations}\par
%  \fi
  \def\@currentaffiliations{}}
\newif\if@ACM@instpresent
\@ACM@instpresenttrue
\newif\if@ACM@citypresent
\@ACM@citypresenttrue
\newif\if@ACM@countrypresent
\@ACM@countrypresenttrue
\def\@ACM@resetaffil{%
  \global\@ACM@instpresentfalse
  \global\@ACM@citypresentfalse
  \global\@ACM@countrypresentfalse
}
\def\@ACM@checkaffil{%
  \if@ACM@instpresent\else
  \ClassWarningNoLine{\@classname}{No institution present for an affiliation}%
  \fi
  \if@ACM@citypresent\else
  \ClassWarningNoLine{\@classname}{No city present for an affiliation}%
  \fi
  \if@ACM@countrypresent\else
  \ClassError{\@classname}{No country present for an affiliation}{ACM
    requires each author to indicate their country using country macro.}%
  \fi
}
\def\@mkauthors@i{%
  \def\@currentauthors{}%
  \def\@currentaffiliations{}%
  \global\let\and\@typeset@author@line
  \def\@author##1{%
    \ifx\@currentauthors\@empty
      \gdef\@currentauthors{\@authorfont\MakeTextUppercase{##1}}%
    \else
       \g@addto@macro{\@currentauthors}{\and\MakeTextUppercase{##1}}%
    \fi
    \gdef\and{}}%
  \def\email##1##2{}%
  \def\affiliation##1##2{%
    \def\@tempa{##2}\ifx\@tempa\@empty\else
       \ifx\@currentaffiliations\@empty
          \gdef\@currentaffiliations{%
            \setkeys{@ACM@affiliation@}{obeypunctuation=false}%
            \setkeys{@ACM@affiliation@}{##1}%
            \@ACM@resetaffil
            \@affiliationfont##2\@ACM@checkaffil}%
       \else
         \g@addto@macro{\@currentaffiliations}{\and
           \setkeys{@ACM@affiliation@}{obeypunctuation=false}%
           \setkeys{@ACM@affiliation@}{##1}\@ACM@resetaffil
           ##2\@ACM@checkaffil}%
      \fi
    \fi
     \global\let\and\@typeset@author@line}%
  \global\setbox\mktitle@bx=\vbox{\noindent\unvbox\mktitle@bx\par\medskip
    \noindent\addresses\@typeset@author@line
   \par\medskip}%
}
\newbox\author@bx
\newdimen\author@bx@wd
\newskip\author@bx@sep
\author@bx@sep=1pc\relax
\def\@typeset@author@bx{\bgroup\hsize=\author@bx@wd
  \def\and{\par}\normalbaselines
  \global\setbox\author@bx=\vtop{\centering
    \@authorfont\@currentauthors\par\@affiliationfont
    \@currentaffiliation}\egroup
  \box\author@bx\hspace{\author@bx@sep}%
  \gdef\@currentauthors{}%
  \gdef\@currentaffiliation{}}

\def\@mkauthorsaddresses{%
  \ifnum\num@authors>1\relax
  Authors' \else Author's \fi
  \ifnum\num@authorgroups>1\relax
  addresses: \else address: \fi
  \bgroup
  \def\streetaddress##1{\unskip, ##1}%
  \def\postcode##1{\unskip, ##1}%
  \def\position##1{\unskip\ignorespaces}%
  \gdef\@ACM@institution@separator{, }%
  \def\institution##1{\unskip\@ACM@institution@separator ##1\gdef\@ACM@institution@separator{ and }}%
  \def\city##1{\unskip, ##1}%
  \def\state##1{\unskip, ##1}%
  \renewcommand\department[2][0]{\unskip\@addpunct, ##2}%
  \def\country##1{\unskip, ##1}%
  \def\and{\unskip; \gdef\@ACM@institution@separator{, }}%
  \def\@author##1{##1}%
  \def\email##1##2{\unskip, \nolinkurl{##2}}%
  \addresses
  \egroup}

\def\@setaddresses{}
\def\@authornotemark{\g@addto@macro\@currentauthors{\footnotemark\relax}}
\def\@@authornotemark#1{\g@addto@macro\@currentauthors{\footnotemark[#1]}}
%% removed teaser support
\def\@mkabstract{\bgroup
  {\phantomsection\addcontentsline{toc}{section}{Abstract}%
   \ignorespaces\getstored[1]{abstracts}\par%
   }%
   \egroup}
\def\@mkswedishabstract{\bgroup
  {\section*{Sammanfattning}
  \phantomsection\addcontentsline{toc}{section}{Sammanfattning}%
  % \ignorespaces\@swedishabstract\par}%
   \ignorespaces\getstored[2]{abstracts}\par%
   }%
  \egroup}
\def\@mkbibcitation{}
\def\@printendtopmatter{%
  \let\@vspace\@vspace@orig
  \let\@vspacer\@vspacer@orig
  \par\bigskip
  \let\@vspace\@vspace@acm
  \let\@vspacer\@vspacer@acm
  }
\def\@setthanks{\long\def\thanks##1{\par##1\@addpunct.}\thankses}
\def\@setauthorsaddresses{\@authorsaddresses\unskip\@addpunct.}
\RequirePackage{fancyhdr}
\let\ACM@ps@plain\ps@plain
\let\ACM@ps@myheadings\ps@myheadings
\let\ACM@ps@headings\ps@headings
\def\ACM@restore@pagestyle{%
  \let\ps@plain\ACM@ps@plain
  \let\ps@myheadings\ACM@ps@myheadings
  \let\ps@headings\ACM@ps@headings}
\AtBeginDocument{\ACM@restore@pagestyle}
\if@ACM@review
  \newsavebox{\ACM@linecount@bx}
  \newlength\ACM@linecount@bxht
  \newcount\ACM@linecount
  \ACM@linecount\@ne\relax
  \def\ACM@mk@linecount{%
    \savebox{\ACM@linecount@bx}[4em][t]{\parbox[t]{4em}{\normalfont
        \normalsize
        \setlength{\ACM@linecount@bxht}{0pt}%
        \loop{\color{red}\scriptsize\the\ACM@linecount}\\
        \global\advance\ACM@linecount by \@ne
        \addtolength{\ACM@linecount@bxht}{\baselineskip}%
        \ifdim\ACM@linecount@bxht<\textheight\repeat
        {\color{red}\scriptsize\the\ACM@linecount}\hfill
        \global\advance\ACM@linecount by \@ne}}}
\fi
\def\ACM@linecountL{%
  \if@ACM@review
  \ACM@mk@linecount
  \begin{picture}(0,0)%
    \put(-26,-22){\usebox{\ACM@linecount@bx}}%
  \end{picture}%
  \fi}

\def\@shortauthors{%
  \shortauthors}
\def\@headfootfont{\sffamily\footnotesize}
\AtBeginDocument{%
\fancypagestyle{standardpagestyle}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{\z@}%
  \renewcommand{\footrulewidth}{\z@}%
  \def\@acmArticlePage{%
    \ifx\@acmArticle\empty%
      \if@ACM@printfolios\thepage\fi%
    \else%
      \@acmArticle\if@ACM@printfolios:\thepage\fi%
    \fi%
  }%
  % Proceedings
    \fancyfoot[C]{\if@ACM@printfolios\footnotesize\thepage\fi}%
    \fancyhead[LO]{\ACM@linecountL\@headfootfont\shorttitle}%
    \fancyhead[RE]{\@headfootfont\@shortauthors}%
    \fancyhead[LE]{\ACM@linecountL}%
    \fancyhead[RO]{}%
}%
\pagestyle{standardpagestyle}
}
\newdimen\@folio@wd
\@folio@wd=\z@
\newdimen\@folio@ht
\@folio@ht=\z@
\newdimen\@folio@voffset
\@folio@voffset=\z@
\def\@folio@max{1}
\ifcase\ACM@format@nr
\relax % manuscript
\or % acmsmall
  \@folio@wd=45.75pt\relax
  \@folio@ht=1.25in\relax
  \@folio@voffset=.2in\relax
  \def\@folio@max{8}
\or % acmlarge
  \@folio@wd=43.25pt\relax
  \@folio@ht=79pt\relax
  \@folio@voffset=.55in\relax
  \def\@folio@max{10}
\fi
\def\@folioblob{\@tempcnta=0\@acmArticleSeq\relax
  \ifnum\@tempcnta=0\relax\else
  \loop
     \ifnum\@tempcnta>\@folio@max\relax
      \advance\@tempcnta by - \@folio@max
   \repeat
    \advance\@tempcnta by -1\relax
    \@tempdima=\@folio@ht\relax
    \multiply\@tempdima by \the\@tempcnta\relax
    \advance\@tempdima by -\@folio@voffset\relax
    \begin{picture}(0,0)
    \makebox[\z@]{\raisebox{-\@tempdima}{%
        \rlap{%
          \raisebox{-0.45\@folio@ht}[\z@][\z@]{%
            \rule{\@folio@wd}{\@folio@ht}}}%
        \parbox{\@folio@wd}{%
          \centering
          \textcolor{white}{\LARGE\sffamily\bfseries\@acmArticle}}}}
  \end{picture}\fi}

\AtBeginDocument{%
\fancypagestyle{firstpagestyle}{%
  \fancyhf{}%
  \renewcommand{\headrulewidth}{\z@}%
  \renewcommand{\footrulewidth}{\z@}%

    \relax % manuscript
      \fancyhead[L]{\ACM@linecountL}%
      \fancyfoot[RO,LE]{\if@ACM@printfolios\small\thepage\fi}%

}}
\def\ACM@NRadjust#1{%
 \begingroup
  \expandafter\ifx\csname Sectionformat\endcsname\relax
  % do nothing when  \Sectionformat  is unknown
   \def\next{\endgroup #1}%
 \else
  \def\next{\endgroup
   \let\realSectionformat\Sectionformat
   \def\ACM@sect@format@{#1}%
   \let\Sectionformat\ACM@NR@adjustedSectionformat
 %%  next lines added 2018-06-17 to ensure section number is styled
   \let\real@adddotafter\@adddotafter
   \let\@adddotafter\ACM@adddotafter
   #1{}% imposes the styles, but nullifies  \MakeUppercase
   \let\@adddotafter\real@adddotafter
  }%
 \fi \next
}
\def\ACM@NR@adjustedSectionformat#1#2{%
 \realSectionformat{\ACM@sect@format{#1}}{#2}%
 \let\Sectionformat\realSectionformat}
\DeclareRobustCommand{\ACM@sect@format}{\ACM@sect@format@}
\def\ACM@sect@format@null#1{#1}
\let\ACM@sect@format@\ACM@sect@format@null
\AtBeginDocument{%
 \expandafter\ifx\csname LTX@adddotafter\endcsname\relax
  \let\LTX@adddotafter\@adddotafter
 \fi
}
\def\ACM@adddotafter#1{\ifx\relax#1\relax\else\LTX@adddotafter{#1}\fi}
\renewcommand\section{\@startsection{section}{1}{\z@}%
  {-.75\baselineskip \@plus -2\p@ \@minus -.2\p@}%
  {.25\baselineskip}%
  {\ACM@NRadjust\@secfont}}
\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%
  {-.75\baselineskip \@plus -2\p@ \@minus -.2\p@}%
  {.25\baselineskip}%
  {\ACM@NRadjust\@subsecfont}}
\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
  {-.5\baselineskip \@plus -2\p@ \@minus -.2\p@}%
  {-3.5\p@}%
  {\ACM@NRadjust{\@subsubsecfont\@adddotafter}}}
\renewcommand\paragraph{\@startsection{paragraph}{4}{\parindent}%
  {-.5\baselineskip \@plus -2\p@ \@minus -.2\p@}%
  {-3.5\p@}%
  {\ACM@NRadjust{\@parfont\@adddotafter}}}
\newcommand\noindentparagraph{\@startsection{paragraph}{4}{\z@}%
  {-.5\baselineskip \@plus -2\p@ \@minus -.2\p@}%
  {-3.5\p@}%
  {\ACM@NRadjust{\@parfont}}}

\renewcommand\part{\@startsection{part}{9}{\z@}%
  {-10\p@ \@plus -4\p@ \@minus -2\p@}%
  {4\p@}%
  {\ACM@NRadjust\@parfont}}
\def\section@raggedright{\@rightskip\@flushglue
  \rightskip\@rightskip
  \leftskip\z@skip
  \parindent\z@}
\def\@secfont{\sffamily\bfseries\section@raggedright\MakeTextUppercase}
\def\@subsecfont{\sffamily\bfseries\section@raggedright}
\def\@subsubsecfont{\sffamily\itshape}
\def\@parfont{\itshape}
\setcounter{secnumdepth}{3}
\ifcase\ACM@format@nr
\relax % manuscript
\or % acmsmall
\or % acmlarge
 \def\@secfont{\sffamily\large\section@raggedright\MakeTextUppercase}
 \def\@subsecfont{\sffamily\large\section@raggedright}
\or % acmtog
 \def\@secfont{\sffamily\large\section@raggedright\MakeTextUppercase}
 \def\@subsecfont{\sffamily\large\section@raggedright}
\or % sigconf
 \def\@secfont{\bfseries\Large\section@raggedright\MakeTextUppercase}
 \def\@subsecfont{\bfseries\Large\section@raggedright}
\fi
\def\@adddotafter#1{#1\@addpunct{.}}
\def\@addspaceafter#1{#1\@addpunct{\enspace}}
\providecommand*\@dotsep{4.5}
\def\@acmplainbodyfont{\itshape}
\def\@acmplainindent{\parindent}
\def\@acmplainheadfont{\scshape}
\def\@acmplainnotefont{\@empty}

\newtheoremstyle{acmplain}%
  {.5\baselineskip\@plus.2\baselineskip
    \@minus.2\baselineskip}% space above
  {.5\baselineskip\@plus.2\baselineskip
    \@minus.2\baselineskip}% space below
  {\@acmplainbodyfont}% body font
  {\@acmplainindent}% indent amount
  {\@acmplainheadfont}% head font
  {.}% punctuation after head
  {.5em}% spacing after head
  {\thmname{#1}\thmnumber{ #2}\thmnote{ {\@acmplainnotefont(#3)}}}% head spec
\def\@acmdefinitionbodyfont{\normalfont}
\def\@acmdefinitionindent{\parindent}
\def\@acmdefinitionheadfont{\itshape}
\def\@acmdefinitionnotefont{\@empty}

\newtheoremstyle{acmdefinition}%
  {.5\baselineskip\@plus.2\baselineskip
    \@minus.2\baselineskip}% space above
  {.5\baselineskip\@plus.2\baselineskip
    \@minus.2\baselineskip}% space below
  {\@acmdefinitionbodyfont}% body font
  {\@acmdefinitionindent}% indent amount
  {\@acmdefinitionheadfont}% head font
  {.}% punctuation after head
  {.5em}% spacing after head
  {\thmname{#1}\thmnumber{ #2}\thmnote{ {\@acmdefinitionnotefont(#3)}}}% head spec
\theoremstyle{acmplain}
\AtEndPreamble{%
  \if@ACM@acmthm
  \theoremstyle{acmplain}
  \@ifundefined{theorem}{%
  \newtheorem{theorem}{Theorem}[section]
  }{}
  \@ifundefined{conjecture}{%
  \newtheorem{conjecture}[theorem]{Conjecture}
  }{}
  \@ifundefined{proposition}{%
  \newtheorem{proposition}[theorem]{Proposition}
  }{}
  \@ifundefined{lemma}{%
  \newtheorem{lemma}[theorem]{Lemma}
  }{}
  \@ifundefined{corollary}{%
  \newtheorem{corollary}[theorem]{Corollary}
  }{}
  \theoremstyle{acmdefinition}
  \@ifundefined{example}{%
  \newtheorem{example}[theorem]{Example}
  }{}
  \@ifundefined{definition}{%
  \newtheorem{definition}[theorem]{Definition}
  }{}
  \fi
  \theoremstyle{acmplain}
}
\def\@proofnamefont{\scshape}
\def\@proofindent{\indent}
\renewenvironment{proof}[1][\proofname]{\par
  \pushQED{\qed}%
  \normalfont \topsep6\p@\@plus6\p@\relax
  \trivlist
  \item[\@proofindent\hskip\labelsep
        {\@proofnamefont #1\@addpunct{.}}]\ignorespaces
}{%
  \popQED\endtrivlist\@endpefalse
}
\AtEndPreamble{%
  \if@ACM@pbalance
    \global\@ACM@balancefalse
    \RequirePackage{pbalance}%
  \fi
  \if@ACM@balance
    \ifcase\ACM@format@nr
    \relax % manuscript
    \global\@ACM@balancefalse
    \or % sigconf
          \RequirePackage{balance}%
    \fi
  \fi
}
\AtEndDocument{%
  \if@ACM@balance
  \if@twocolumn
  \balance
  \fi\fi}
\newcommand\acksname{Acknowledgments}
\specialcomment{acks}{%
  \begingroup
  \section*{\acksname}
  \phantomsection\addcontentsline{toc}{section}{\acksname}
}{%
  \endgroup
}
\def\grantsponsor#1#2#3{#2}
\newcommand\grantnum[3][]{#3%
  \def\@tempa{#1}\ifx\@tempa\@empty\else\space(\url{#1})\fi}
\AtEndPreamble{%
\if@ACM@screen
  \includecomment{screenonly}
  \excludecomment{printonly}
\else
  \excludecomment{screenonly}
  \includecomment{printonly}
\fi
\includecomment{anonsuppress}
}
\newcommand\showeprint[2][arxiv]{%
  \def\@tempa{#1}%
  \ifx\@tempa\@empty\def\@tempa{arxiv}\fi
  \def\@tempb{arxiv}%
  \ifx\@tempa\@tempb\relax
     arXiv:\href{https://arxiv.org/abs/#2}{#2}%
  \else
     \def\@tempb{arXiv}%
     \ifx\@tempa\@tempb\relax
       arXiv:\href{https://arxiv.org/abs/#2}{#2}%
     \else
       arXiv:#2%
    \fi
  \fi}
\def\theindex{\@restonecoltrue\if@twocolumn\@restonecolfalse\fi
  \columnseprule\z@ \columnsep 35\p@
  \@indextitlestyle
  \let\item\@idxitem
  \parindent\z@  \parskip\z@\@plus.3\p@\relax
  \raggedright
  \hyphenpenalty\@M
  \footnotesize}
\let\@vspace@orig=\@vspace
\let\@vspacer@orig=\@vspacer
%\apptocmd{\@vspace}{\ClassWarning{\@classname}{\string\vspace\space should
%    only be used to provide space above/below surrounding
%    objects}}{}{}
%\apptocmd{\@vspacer}{\ClassWarning{\@classname}{\string\vspace\space should
%    only be used to provide space above/below surrounding
%    objects}}{}{}
\let\@vspace@acm=\@vspace
\let\@vspacer@acm=\@vspacer
\let\ACM@origbaselinestretch\baselinestretch
\AtEndDocument{\ifx\baselinestretch\ACM@origbaselinestretch\else
  \ClassError{\@classname}{An attempt to redefine
    \string\baselinestretch\space detected.  Please do not do this for
    ACM submissions!}\fi}
\normalsize\normalfont\frenchspacing

%%
%% Additions for the meta data for the template
\let\@hostcompany\@empty
\newcommand{\hostcompany}[1]{\def\@hostcompany{#1}}
\let\@hostorganization\@empty
\newcommand{\hostorganization}[1]{\def\@hostorganization{#1}}

% First author's information
\let\@authorsLastname\@empty
\newcommand{\authorsLastname}[1]{\def\@authorsLastname{#1}}
\let\@authorsFirstname\@empty
\newcommand{\authorsFirstname}[1]{\def\@authorsFirstname{#1}}
\let\@email\@empty
\newcommand{\firstemail}[1]{\def\@email{#1}}
\let\@kthid\@empty
\newcommand{\kthid}[1]{\def\@kthid{#1}}
%\let\@orcid\@empty
%\newcommand{\orcid}[1]{\def\@orcid{#1}}
\let\@authorsSchool\@empty
\newcommand{\authorsSchool}[1]{\def\@authorsSchool{#1}}
\let\@authorsDepartment\@empty
\newcommand{\authorsDepartment}[1]{\def\@authorsDepartment{#1}}
% Information about the city and country for the acknowledgement
\let\@authorCity\@empty
\newcommand{\authorCity}[1]{\def\@authorCity{#1}}
\let\@authorCountry\@empty
\newcommand{\authorCountry}[1]{\def\@authorCountry{#1}}
\let\@authorCityCountryDate\@empty
% Define the command so that if a date is not specified it will not output the comma; it only outputs the comma if there is a date.
\ExplSyntaxOn
\cs_set_eq:NN  \IfEmptyTF  \tl_if_blank:nTF
\ExplSyntaxOff
\NewDocumentCommand{\authorCityCountryDate}{m}{
\def\@authorCityCountryDate{\ifx\@authorCity\@empty%
    Stockholm%
    \else%
    \ifx\@authorCountry\@empty%
    \@authorCity%
    \else%
    \@authorCity, \@authorCountry%
    \fi%
    \fi%
    \IfEmptyTF{#1}{}{, #1}%
    }%
}
\authorCityCountryDate{\MONTH\enspace\the\year} % default month and year for the acknowledgement signature

% Second author's information
\let\@secondAuthorsLastname\@empty
\newcommand{\secondAuthorsLastname}[1]{\def\@secondAuthorsLastname{#1}}
\let\@secondAuthorsFirstname\@empty
\newcommand{\secondAuthorsFirstname}[1]{\def\@secondAuthorsFirstname{#1}}
\let\@secondemail\@empty
\newcommand{\secondemail}[1]{\def\@secondemail{#1}}
\let\@secondkthid\@empty
\newcommand{\secondkthid}[1]{\def\@secondkthid{#1}}
%\let\@secondorcid\@empty
%\newcommand{\secondorcid}[1]{\def\@secondorcid{#1}}
\let\@secondAuthorsSchool\@empty
\newcommand{\secondAuthorsSchool}[1]{\def\@secondAuthorsSchool{#1}}
\let\@secondAuthorsDepartment\@empty
\newcommand{\secondAuthorsDepartment}[1]{\def\@secondAuthorsDepartment{#1}}
% Information about the city and country for the acknowledgement
\let\@secondAuthorCity\@empty
\newcommand{\secondAuthorCity}[1]{\def\@secondAuthorCity{#1}}
\let\@secondAuthorCountry\@empty
\newcommand{\secondAuthorCountry}[1]{\def\@secondAuthorCountry{#1}}
\let\@secondAuthorCityCountryDate\@empty
% Define the command so if a date is not specified it will not output the comma; it only outputs the comma if there is a date.
\NewDocumentCommand{\secondAuthorCityCountryDate}{m}{
\def\@secondAuthorCityCountryDate{\ifx\@secondAuthorCity\@empty%
    Stockholm%
    \else%
    \ifx\@secondAuthorCountry\@empty%
    \@secondAuthorCity%
    \else%
    \@secondAuthorCity, \@secondAuthorCountry%
    \fi%
    \fi%
    \IfEmptyTF{#1}{}{, #1}%%
    }%
}

\let\@supervisorAsLastname\@empty
\newcommand{\supervisorAsLastname}[1]{\def\@supervisorAsLastname{#1}}
\let\@supervisorAsFirstname\@empty
\newcommand{\supervisorAsFirstname}[1]{\def\@supervisorAsFirstname{#1}}
\let\@supervisorAsEmail\@empty
\newcommand{\supervisorAsEmail}[1]{\def\@supervisorAsEmail{#1}}
\let\@supervisorAsKTHID\@empty
\newcommand{\supervisorAsKTHID}[1]{\def\@supervisorAsKTHID{#1}}
\let\@supervisorAsOrganization\@empty
\newcommand{\supervisorAsOrganization}[1]{\def\@supervisorAsOrganization{#1}}
\let\@supervisorAsSchool\@empty
\newcommand{\supervisorAsSchool}[1]{\def\@supervisorAsSchool{#1}}
\let\@supervisorAsDepartment\@empty
\newcommand{\supervisorAsDepartment}[1]{\def\@supervisorAsDepartment{#1}}

\let\@supervisorBsLastname\@empty
\newcommand{\supervisorBsLastname}[1]{\def\@supervisorBsLastname{#1}}
\let\@supervisorBsFirstname\@empty
\newcommand{\supervisorBsFirstname}[1]{\def\@supervisorBsFirstname{#1}}
\let\@supervisorBsEmail\@empty
\newcommand{\supervisorBsEmail}[1]{\def\@supervisorBsEmail{#1}}
\let\@supervisorBsKTHID\@empty
\newcommand{\supervisorBsKTHID}[1]{\def\@supervisorBsKTHID{#1}}
\let\@supervisorBsOrganization\@empty
\newcommand{\supervisorBsOrganization}[1]{\def\@supervisorBsOrganization{#1}}
\let\@supervisorBsSchool\@empty
\newcommand{\supervisorBsSchool}[1]{\def\@supervisorBsSchool{#1}}
\let\@supervisorBsDepartment\@empty
\newcommand{\supervisorBsDepartment}[1]{\def\@supervisorBsDepartment{#1}}

\let\@supervisorCsLastname\@empty
\newcommand{\supervisorCsLastname}[1]{\def\@supervisorCsLastname{#1}}
\let\@supervisorCsFirstname\@empty
\newcommand{\supervisorCsFirstname}[1]{\def\@supervisorCsFirstname{#1}}
\let\@supervisorCsEmail\@empty
\newcommand{\supervisorCsEmail}[1]{\def\@supervisorCsEmail{#1}}
\let\@supervisorCsKTHID\@empty
\newcommand{\supervisorCsKTHID}[1]{\def\@supervisorCsKTHID{#1}}
\let\@supervisorCsOrganization\@empty
\newcommand{\supervisorCsOrganization}[1]{\def\@supervisorCsOrganization{#1}}
\let\@supervisorCsSchool\@empty
\newcommand{\supervisorCsSchool}[1]{\def\@supervisorCsSchool{#1}}
\let\@supervisorCsDepartment\@empty
\newcommand{\supervisorCsDepartment}[1]{\def\@supervisorCsDepartment{#1}}

\let\@examinersLastname\@empty
\newcommand{\examinersLastname}[1]{\def\@examinersLastname{#1}}
\let\@examinersFirstname\@empty
\newcommand{\examinersFirstname}[1]{\def\@examinersFirstname{#1}}
\let\@examinersEmail\@empty
\newcommand{\examinersEmail}[1]{\def\@examinersEmail{#1}}
\let\@examinersKTHID\@empty
\newcommand{\examinersKTHID}[1]{\def\@examinersKTHID{#1}}
\let\@examinersOrganization\@empty
\newcommand{\examinersOrganization}[1]{\def\@examinersOrganization{#1}}
\let\@examinersSchool\@empty
\newcommand{\examinersSchool}[1]{\def\@examinersSchool{#1}}
\let\@examinersDepartment\@empty
\newcommand{\examinersDepartment}[1]{\def\@examinersDepartment{#1}}

\let\@courseCycle\@empty
\newcommand{\courseCycle}[1]{\def\@courseCycle{#1}}
\let\@courseCode\@empty
\newcommand{\courseCode}[1]{\def\@courseCode{#1}}
\let\@courseCredits\@empty
\newcommand{\courseCredits}[1]{\def\@courseCredits{#1}}

\let\@degreeName\@empty
\newcommand{\degreeName}[1]{\def\@degreeName{#1}}
\let\@subjectArea\@empty
\newcommand{\subjectArea}[1]{\def\@subjectArea{#1}}

\let\@secondDegreeName\@empty
\newcommand{\secondDegreeName}[1]{\def\@secondDegreeName{#1}}
\let\@secondSubjectArea\@empty
\newcommand{\secondSubjectArea}[1]{\def\@secondSubjectArea{#1}}

% Data related to the oral presentation
\let\@presentationDateAndTimeISO\@empty
\newcommand{\presentationDateAndTimeISO}[1]{\def\@presentationDateAndTimeISO{#1}}
\let\@presentationLanguage\@empty
\newcommand{\presentationLanguage}[1]{\def\@presentationLanguage{#1}}
\let\@presentationRoom\@empty
\newcommand{\presentationRoom}[1]{\def\@presentationRoom{#1}}
\let\@presentationAddress\@empty
\newcommand{\presentationAddress}[1]{\def\@presentationAddress{#1}}
\let\@presentationCity\@empty
\newcommand{\presentationCity}[1]{\def\@presentationCity{#1}}

\let\@opponentsNames\@empty
\newcommand{\opponentsNames}[1]{\def\@opponentsNames{#1}}

% Data for DIVA National Subject Cateories fields
\let\@nationalsubjectcategories\@empty
\newcommand{\nationalsubjectcategories}[1]{\def\@nationalsubjectcategories{#1}}

% Keywords
\let\@EnglishKeywords\@empty
\newcommand{\EnglishKeywords}[1]{\def\@EnglishKeywords{#1}}

% Defined above
%\let\@SwedishKeywords\@empty
%\newcommand{\SwedishKeywords}[1]{\def\@SwedishKeywords{#1}}

\ExplSyntaxOn
\cs_new_eq:NN \strcompare \str_if_eq:nnTF
\ExplSyntaxOff


%% Changed to use expl3 strcompare rather than xstring's IfEqCase, since the later is not expandable
%% The insight for this is from Enrico Gregorio - egreg's posing of 26 April 2016 at 
%% https://tex.stackexchange.com/questions/306484/how-do-i-perform-an-expandable-string-comparison

\newcommand{\InsertKeywords}[1]{
\strcompare{#1}{english}{\@EnglishKeywords}{}%
\strcompare{#1}{swedish}{\@SwedishKeywords}{}%
}

% Get and store information about the series and the number within this series, i.e, TRITA numbers
%"Series": \{
%	"Title of series": "TRITA-ICT-EX",
%	"No. in series": "2019:00"
\let\@thesisSeries\@empty
\let\@thesisSeriesNumber\@empty
\newcommand{\trita}[2]{\def\@thesisSeries{#1}\def\@thesisSeriesNumber{#2}}

\let\@programcode\@empty
\newcommand{\programcode}[1]{%
\def\@programcode{#1}%
\edef\@prgmcode{\programmecode{#1}}}

\let\@secondProgramcode\@empty
\newcommand{\secondProgramcode}[1]{%
\def\@secondProgramcode{#1}%
\edef\@secondprgmcode{\programmecode{#1}}}

\let\@edprogram\@empty
\newcommand{\edprogram}[1]{%
\def\@edprogram{#1}}

\let\@secondedProgram\@empty
\newcommand{\secondedProgram}[1]{%
\def\@secondedProgram{#1}}



% get all of the information about the school codes and program codes
\input{lib/schools_and_programs.ins}



\makeatletter


\newcommand\protected@iwrite[3]{%
  \begingroup
  \let\thepage\relax
  #2%
  \let\protect\@unexpandable@protect
  \edef\reserved@a{\immediate\write #1{#3}}%
  \reserved@a
  \endgroup
  \if@nobreak\ifvmode\nobreak\fi\fi
}

\newcommand{\divainfo}[1]{
\thispagestyle{empty}
    \sffamily\tiny
    \begin{flushleft}
    \{\\
        "Author1": \{ \ifx\@authorsLastname\@empty\relax
     \else
     "Last name": "\@authorsLastname",\\
     \fi
     \ifx\@authorsFirstname\@empty\relax
     \else
     "First name": "\@authorsFirstname",\\
     \fi
     \ifx\@kthid\@empty\relax
     \else
     "Local User Id": "\@kthid",\\
     \fi
     \ifx\@email\@empty\relax
     \else
     "E-mail": "\@email",\\
     \fi
     \ifx\@authorsSchool\@empty\relax
     \else
     "organisation": \{"L1": "\@authorsSchool",\\
     \ifx\@authorsDepartment\@empty\relax
     \else
     ,"L2": "\@authorsDepartment"
     \fi
     \}\\
     \fi
    \},\\
    \ifx\@secondAuthorsLastname\@empty\relax
    \else
        "Author2": \{ \ifx\@secondAuthorsLastname\@empty\relax
            \else
        "Last name": "\@secondAuthorsLastname",\\
        \fi
        \ifx\@secondAuthorsFirstname\@empty\relax
            \else
        "First name": "\@secondAuthorsFirstname",\\
        \fi
        \ifx\@secondkthid\@empty\relax
            \else
        "Local User Id": "\@secondkthid",\\
        \fi
        \ifx\@secondemail\@empty\relax
            \else
        "E-mail": "\@secondemail",\\
        \fi
        \ifx\@secondAuthorsSchool\@empty\relax
        \else
        "organisation": \{"L1": "\@secondAuthorsSchool",\\
        \ifx\@secondAuthorsDepartment\@empty\relax
        \else
        "L2": "\@secondAuthorsDepartment"
        \fi
        \}\\
		\fi
    \},\\
    \fi
    \ifx\@courseCycle\@empty\relax
    \else
    "Cycle": "\@courseCycle",\\
    \fi
    \ifx\@courseCode\@empty\relax
    \else
    "Course code": "\@courseCode",\\
    \fi
    \ifx\@courseCredits\@empty\relax
    \else
    "Credits": "\@courseCredits",\\
     \fi

       "Degree1": \{"Educational program": "\@prgmcode"\\ % 
       \ifx\@programcode\@empty\relax
       \else
       ,"programcode": "\@programcode"\\
       \fi

        \ifx\@degreeName\@empty\relax
       \else
       ,"Degree": "\@degreeName"\\
       \fi
        \ifx\@subjectArea\@empty\relax
       \else
       ,"subjectArea": "\@subjectArea"\\
       \fi
       \},\\
       \ifx\@secondProgramcode\@empty\relax            %% If there is a second program code then add this element
       \else
        "Degree2": \{"Educational program": "\@secondprgmcode"\\
        \ifx\@secondProgramcode\@empty\relax
         \else
         ,"programcode": "\@secondProgramcode"\\
         \fi
         \ifx\@secondDegreeName\@empty\relax
        \else
        ,"Degree": "\@secondDegreeName"\\
        \fi
            \ifx\@secondSubjectArea\@empty\relax
        \else
         ,"SubjectArea": "\@secondSubjectArea"\\
         \fi
         \},\\
       \fi
       "Title": \{\\
       "Main title": "\@title",\\
       \ifx\@subtitle\@empty\relax
       \else
       "Subtitle": "\@subtitle",\\
       \fi
       "Language": "eng"
       \},\\
    "Alternative title": \{\\
    "Main title": "\@alttitle",\\
    \ifx\@altsubtitle\@empty\relax
    \else
    "Subtitle": "\@altsubtitle",\\
    \fi
    "Language": "swe"\\
    \},\\
     \ifx\@supervisorAsLastname\@empty\relax
        \else
    "Supervisor1": \{ "Last name": "\@supervisorAsLastname",\\
    \ifx\@supervisorAsFirstname\@empty\relax
    \else
    "First name": "\@supervisorAsFirstname",\\
    \fi
    \ifx\@supervisorAsKTHID\@empty\relax
    \else
    "Local User Id": "\@supervisorAsKTHID",\\
    \fi
    \ifx\@supervisorAsEmail\@empty\relax
    \else
    "E-mail": "\@supervisorAsEmail",\\
    \fi
    \ifx\@supervisorAsOrganization\@empty
    \ifx\@supervisorAsSchool\@empty\relax
    \else
    "organisation": \{"L1": "\@supervisorAsSchool",\\
    \ifx\@supervisorAsDepartment\@empty\relax
    \else
    "L2": "\@supervisorAsDepartment"
    \fi
    \}\\
    \fi
    \else
    "Other organisation": "\@supervisorAsOrganization"\\
    \fi
    \},\\
    \fi
    \ifx\@supervisorBsLastname\@empty\relax
    \else
    "Supervisor2": \{ "Last name": "\@supervisorBsLastname",\\
    \ifx\@supervisorBsFirstname\@empty\relax
    \else
    "First name": "\@supervisorBsFirstname",\\
    \fi
    \ifx\@supervisorBsKTHID\@empty\relax
    \else
    "Local User Id": "\@supervisorBsKTHID",\\
    \fi
    \ifx\@supervisorBsEmail\@empty\relax
    \else
    "E-mail": "\@supervisorBsEmail",\\
    \fi
    \ifx\@supervisorBsOrganization\@empty
    \ifx\@supervisorBsSchool\@empty\relax
    \else
    "organisation": \{"L1": "\@supervisorBsSchool",\\
    \ifx\@supervisorBsDepartment\@empty\relax
    \else
    "L2": "\@supervisorBsDepartment"
    \fi
    \}\\
    \fi
    \else
    "Other organisation": "\@supervisorBsOrganization"\\
    \fi
    \},\\
    \fi
        \ifx\@supervisorCsLastname\@empty\relax
    \else
    "Supervisor3": \{ "Last name": "\@supervisorCsLastname",\\
    \ifx\@supervisorCsFirstname\@empty\relax
    \else
    "First name": "\@supervisorCsFirstname",\\
    \fi
    \ifx\@supervisorCsKTHID\@empty\relax
    \else
    "Local User Id": "\@supervisorCsKTHID",\\
    \fi
    \ifx\@supervisorCsEmail\@empty\relax
    \else
    "E-mail": "\@supervisorCsEmail",\\
    \fi
    \ifx\@supervisorCsOrganization\@empty
    \ifx\@supervisorCsSchool\@empty\relax
    \else
    "organisation": \{"L1": "\@supervisorCsSchool",\\
    \ifx\@supervisorCsDepartment\@empty\relax
    \else
    "L2": "\@supervisorCsDepartment"
    \fi
    \}\\
    \fi
    \else
    "Other organisation": "\@supervisorCsOrganization"\\
    \fi
    \},\\
    \fi
    \ifx\@examinersLastname\@empty\relax
        \else
    "Examiner1": \{ "Last name": "\@examinersLastname",\\
    \ifx\@examinersFirstname\@empty\relax
    \else
    "First name": "\@examinersFirstname",\\
    \fi
    \ifx\@examinersKTHID\@empty\relax
    \else
    "Local User Id": "\@examinersKTHID",\\
    \fi
    \ifx\@examinersEmail\@empty\relax
    \else
    "E-mail": "\@examinersEmail",\\
    \fi
    \ifx\@examinersOrganization\@empty
    \ifx\@examinersSchool\@empty\relax
    \else
    "organisation": \{"L1": "\@examinersSchool",\\
    \ifx\@examinersDepartment\@empty\relax
    \else
    "L2": "\@examinersDepartment"
    \fi
    \}\\
    \fi
    \else
    "Other organisation": "\@examinersOrganization"\}\\
    \fi
    \},\\
    \fi
    \ifx\@hostcompany\@empty\relax
    \else
    "Cooperation": \{ "Partner\_name": "\@hostcompany"\},\\
    \fi
    \ifx\@nationalsubjectcategories\@empty\relax
    \else
    \textquotedbl\relax National Subject Categories\textquotedbl\relax: \textquotedbl\relax\@nationalsubjectcategories\textquotedbl\relax,\\
    \fi
    % \ifx\@hostorganization\@empty\relax\else Host organization: \@hostorganization\\\fi
    "Other information": \{"Year": "\the\year", "Number of pages": \char`\"\pageref{#1}\char`\"
    \},\\
    "Series": \{
    \ifx\@thesisSeries\@empty\relax
        \else
        	"Title of series": "\@thesisSeries"
        	\ifx\@thesisSeriesNumber\@empty\relax
            \else
            , "No. in series": "\@thesisSeriesNumber"
             \fi
    \fi
    \},\\
        \ifx\@opponentsNamea\@empty\relax
        \else
    "Opponents": \{ "Name": "\@opponentsNames"\},\\
       \fi
        \ifx\@presentationDateAndTimeISO\@empty\relax
        \else
       "Presentation": \{ "Date": "\@presentationDateAndTimeISO"\par
        \ifx\@presentationLanguage\@empty\relax
        \else
        ,"Language":"\@presentationLanguage"\par
        \fi
        \ifx\@presentationRoom\@empty\relax
        \else
        ,"Room": "\@presentationRoom"\par
        \fi
        \ifx\@presentationAddress\@empty\relax
        \else
        ,"Address": "\@presentationAddress"\par
        \fi
        \ifx\@presentationCity\@empty\relax
        \else
        ,"City": "\@presentationCity"
        \fi
        \},\par
    \fi
    "Number of lang instances": \textquotedbl 2\textquotedbl\relax,\\
      "Abstract[eng]": €€€€\\
     \typestoredx{1}{abstracts}
      €€€€,\\
      "Keywords[eng]": €€€€\\
      \@keywords\\
      €€€€,\\
     "Abstract[swe]": €€€€\\
    %\ignorespaces\@swedishabstract\\
\ifxeorlua    
    \typestoredx{2}{abstracts}
\else
    %% pdfLaTeX has problems with the Swedish characters with typestoredx
    %% The Swedish characters have to be added to the list of literate 
    %% translations in lib/includes.tex
    %% This works because the typestoredx outputs the characters to a listing environment
    \typestoredx{2}{abstracts}
\fi
      €€€€,\\
      "Keywords[swe]": €€€€\\
      \@SwedishKeywords\\
      €€€€,\\
   \}
   \end{flushleft}
\clearpage

\makeatletter
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% for writing to a JSON file
\newwrite\jsonfile
\immediate\openout\jsonfile=fordiva.json
\immediate\write\jsonfile{\@charlb}
\immediate\write\jsonfile{"Author1": \@charlb \ifx\@authorsLastname\@empty%\relax
     \else
     "Last name": "\@authorsLastname",
     \fi
     \ifx\@authorsFirstname\@empty%\relax
     \else
     "First name": "\@authorsFirstname",
     \fi
     \ifx\@kthid\@empty%\relax
     \else
     "Local User Id": "\@kthid",
     \fi
     \ifx\@email\@empty%\relax
     \else
     "E-mail": "\@email",
     \fi
     \ifx\@authorsSchool\@empty%\relax
     \else
     "organisation": \@charlb"L1": "\@authorsSchool"
     \ifx\@authorsDepartment\@empty%\relax
     \else
     ,"L2": "\@authorsDepartment"
     \fi
     \@charrb
     \fi
\@charrb,}
\ifx\@secondAuthorsLastname\@empty\relax
\else
\immediate\write\jsonfile{
        "Author2": \@charlb \ifx\@secondAuthorsLastname\@empty%\relax
            \else
        "Last name": "\@secondAuthorsLastname",
        \fi
        \ifx\@secondAuthorsFirstname\@empty%\relax
            \else
        "First name": "\@secondAuthorsFirstname",
        \fi
        \ifx\@secondkthid\@empty%\relax
            \else
        "Local User Id": "\@secondkthid",
        \fi
        \ifx\@secondemail\@empty%\relax
            \else
        "E-mail": "\@secondemail",
        \fi
        \ifx\@secondAuthorsSchool\@empty%\relax
        \else
        "organisation": \@charlb"L1": "\@secondAuthorsSchool"
        \ifx\@secondAuthorsDepartment\@empty%\relax
        \else
        ,"L2": "\@secondAuthorsDepartment"
        \fi
        \@charrb
		\fi
\@charrb,}
\fi % end of conditional for secondAuthorsLastname
\immediate\write\jsonfile{\ifx\@courseCycle\@empty%\relax
\else
"Cycle": "\@courseCycle",
\fi
\ifx\@courseCode\@empty%\relax
\else
"Course code": "\@courseCode",
\fi
\ifx\@courseCredits\@emptyv
\else
"Credits": "\@courseCredits",
\fi
}
\immediate\write\jsonfile{"Degree1": \@charlb"Educational program": "\@prgmcode"% 
       \ifx\@programcode\@empty%\relax
       \else
       ,"programcode": "\@programcode"
       \fi
        \ifx\@degreeName\@empty%\relax
       \else
       ,"Degree": "\@degreeName"
       \fi
        \ifx\@subjectArea\@empty%\relax
       \else
       ,"subjectArea": "\@subjectArea"
       \fi
       \@charrb,
       }
       \ifx\@secondProgramcode\@empty%\relax           %% If there is a second program code then add this element
       \else
        \immediate\write\jsonfile{
        "Degree2": \@charlb"Educational program": "\@secondprgmcode" %
        \ifx\@secondProgramcode\@empty%\relax
         \else
         ,"programcode": "\@secondProgramcode"
         \fi
         \ifx\@secondDegreeName\@empty%\relax
        \else
        ,"Degree": "\@secondDegreeName"
        \fi
            \ifx\@secondSubjectArea\@empty%\relax
        \else
         ,"SubjectArea": "\@secondSubjectArea"
         \fi
         \@charrb,\\
       }
     \fi
\immediate\write\jsonfile{"Title": \@charlb
       "Main title": "\@title",
       \ifx\@subtitle\@empty%\relax
       \else
       "Subtitle": "\@subtitle",
       \fi
       "Language": "eng"
       \@charrb,
    "Alternative title": \@charlb
    "Main title": "\@alttitle",
    \ifx\@altsubtitle\@empty%\relax
    \else
    "Subtitle": "\@altsubtitle",
    \fi
    "Language": "swe"
    \@charrb,
}
\ifx\@supervisorAsLastname\@emptyv
        \else
\immediate\write\jsonfile{"Supervisor1": \@charlb "Last name": "\@supervisorAsLastname",
    \ifx\@supervisorAsFirstname\@emptyv
    \else
    "First name": "\@supervisorAsFirstname",
    \fi
    \ifx\@supervisorAsKTHID\@empty%\relax
    \else
    "Local User Id": "\@supervisorAsKTHID",
    \fi
    \ifx\@supervisorAsEmail\@empty%\relax
    \else
    "E-mail": "\@supervisorAsEmail",
    \fi
    \ifx\@supervisorAsOrganization\@empty
    \ifx\@supervisorAsSchool\@empty%\relax
    \else
    "organisation": \@charlb"L1": "\@supervisorAsSchool"
    \ifx\@supervisorAsDepartment\@empty%\relax
    \else
    ,"L2": "\@supervisorAsDepartment"
    \fi
    \@charrb
    \fi
    \else
    "Other organisation": "\@supervisorAsOrganization"
    \fi
    \@charrb,
}
\fi
\ifx\@supervisorBsLastname\@empty%\relax
\else
\immediate\write\jsonfile{"Supervisor2": \@charlb "Last name": "\@supervisorBsLastname",
    \ifx\@supervisorBsFirstname\@empty%\relax
    \else
    "First name": "\@supervisorBsFirstname",
    \fi
    \ifx\@supervisorBsKTHID\@empty%\relax
    \else
    "Local User Id": "\@supervisorBsKTHID",
    \fi
    \ifx\@supervisorBsEmail\@empty%\relax
    \else
    "E-mail": "\@supervisorBsEmail",
    \fi
    \ifx\@supervisorBsOrganization\@empty
    \ifx\@supervisorBsSchool\@empty%\relax
    \else
    "organisation": \@charlb"L1": "\@supervisorBsSchool"
    \ifx\@supervisorBsDepartment\@empty%\relax
    \else
    ,"L2": "\@supervisorBsDepartment"
    \fi
    \@charrb
    \fi
    \else
    "Other organisation": "\@supervisorBsOrganization"
    \fi
    \@charrb,
}
\fi
\ifx\@supervisorCsLastname\@empty%\relax
\else
\immediate\write\jsonfile{"Supervisor3": \@charlb "Last name": "\@supervisorCsLastname",
    \ifx\@supervisorCsFirstname\@empty%\relax
    \else
    "First name": "\@supervisorCsFirstname",
    \fi
    \ifx\@supervisorCsKTHID\@empty%\relax
    \else
    "Local User Id": "\@supervisorCsKTHID",
    \fi
    \ifx\@supervisorCsEmail\@empty%\relax
    \else
    "E-mail": "\@supervisorCsEmail",
    \fi
    \ifx\@supervisorCsOrganization\@empty
    \ifx\@supervisorCsSchool\@empty%\relax
    \else
    "organisation": \@charlb"L1": "\@supervisorCsSchool"
    \ifx\@supervisorCsDepartment\@empty%\relax
    \else
    ,"L2": "\@supervisorCsDepartment"
    \fi
    \@charrb
    \fi
    \else
    "Other organisation": "\@supervisorCsOrganization"
    \fi
    \@charrb,
}
\fi
\ifx\@examinersLastname\@empty%\relax
\else
\immediate\write\jsonfile{"Examiner1": \@charlb "Last name": "\@examinersLastname",
    \ifx\@examinersFirstname\@empty%\relax
    \else
    "First name": "\@examinersFirstname",
    \fi
    \ifx\@examinersKTHID\@empty%\relax
    \else
    "Local User Id": "\@examinersKTHID",
    \fi
    \ifx\@examinersEmail\@empty%\relax
    \else
    "E-mail": "\@examinersEmail",
    \fi
    \ifx\@examinersOrganization\@empty
    \ifx\@examinersSchool\@empty%\relax
    \else
    "organisation": \@charlb"L1": "\@examinersSchool"
    \ifx\@examinersDepartment\@empty%\relax
    \else
    ,"L2": "\@examinersDepartment"
    \fi
    \@charrb
    \fi
    \else
    "Other organisation": "\@examinersOrganization"\@charrb
    \fi
    \@charrb,
}
\fi
\immediate\write\jsonfile{\ifx\@hostcompany\@empty%\relax
\else
"Cooperation": \@charlb "Partner_name": "\@hostcompany"\@charrb,
\fi
}
\ifx\@nationalsubjectcategories\@empty%\relax
\else
\immediate\write\jsonfile{"National Subject Categories": "\@nationalsubjectcategories",
}
\fi
% \ifx\@hostorganization\@empty\relax\else Host organization: \@hostorganization\\\fi
% "\pageref{pg:lastPageofPreface},\pageref{pg:lastPageofMainmatter}" \@charrb,
% Note that the TIMTM theses for not have preface pages
\immediate\write\jsonfile{"Other information": \@charlb"Year": "\the\year", "Number of pages": 
    "\getpagerefnumber{pg:lastPageofMainmatter}" \@charrb,
}
\immediate\write\jsonfile{"Series": \@charlb
    \ifx\@thesisSeries\@empty\relax,
        \else
        	"Title of series": "\@thesisSeries"
        	\ifx\@thesisSeriesNumber\@empty\relax
            \else
            , "No. in series": "\@thesisSeriesNumber"
             \fi
    \fi
    \@charrb,
}
\ifx\@opponentsNamea\@empty\relax
\else
\immediate\write\jsonfile{"Opponents": \@charlb "Name": "\@opponentsNames"\@charrb,
}
\fi
\ifx\@presentationDateAndTimeISO\@empty%\relax,
\else
\immediate\write\jsonfile{"Presentation": \@charlb "Date": "\@presentationDateAndTimeISO"
        \ifx\@presentationLanguage\@empty%\relax,
        \else
        ,"Language": "\@presentationLanguage"
        \fi
        \ifx\@presentationRoom\@empty%
        \else
        ,"Room": "\@presentationRoom"
        \fi
        \ifx\@presentationAddress\@empty%\relax,
        \else
        ,"Address": "\@presentationAddress"
        \fi
        \ifx\@presentationCity\@empty%\relax,
        \else
        ,"City": "\@presentationCity"
        \fi
        \@charrb,
}
\fi
\immediate\write\jsonfile{"Number of lang instances": "2",}
% pdflatex cannot handle the abstracts or the keywords in the code below,
% it generates a "! TeX capacity exceeded, sorry [input stack size=5000]." 
% error message.
\ifxeorlua
\immediate\write\jsonfile{"abstracts": \@charlb}
  \immediate\write\jsonfile{"eng": €€€€}
  %\immediate\write\jsonfile{"\@abstract"}
  \immediate\write\jsonfile{"\qgetstored{1}{abstracts}"}
  \immediate\write\jsonfile{€€€€,}
    \immediate\write\jsonfile{"swe": €€€€}
 % \immediate\write\jsonfile{"\@swedishabstract"}
  \immediate\write\jsonfile{"\qgetstored{2}{abstracts}"}
  \immediate\write\jsonfile{€€€€,}
\immediate\write\jsonfile{\@charrb,} % end the abstracts dict

\immediate\write\jsonfile{"keywords": \@charlb}
    \immediate\write\jsonfile{"eng": €€€€}
    \immediate\write\jsonfile{"\@keywords"}
    \immediate\write\jsonfile{€€€€,}
    \immediate\write\jsonfile{"swe": €€€€}
    \immediate\write\jsonfile{"\@SwedishKeywords"}
    \immediate\write\jsonfile{€€€€,}

    \immediate\write\jsonfile{\@charrb} % end the keywords dict
\else

\immediate\write\jsonfile{"abstracts": \@charlb}
  \immediate\write\jsonfile{"eng": }
  %\immediate\write\jsonfile{"\@abstract"}
  \immediate\write\jsonfile{"\qgetstored{1}{abstracts}"}
  \immediate\write\jsonfile{,}
    \immediate\write\jsonfile{"swe": }
  %\immediate\write\jsonfile{"\@swedishabstract"}
    \immediate\write\jsonfile{"\qgetstored{2}{abstracts}"}
  \immediate\write\jsonfile{,}
\immediate\write\jsonfile{\@charrb,} % end the abstracts dict

\immediate\write\jsonfile{"keywords": \@charlb}
    \immediate\write\jsonfile{"eng": }
    \immediate\write\jsonfile{"\@keywords"}
    \immediate\write\jsonfile{,}
    \immediate\write\jsonfile{"swe": }
    \immediate\write\jsonfile{"\@SwedishKeywords"}
    \immediate\write\jsonfile{,}

    \immediate\write\jsonfile{\@charrb} % end the keywords dict


    \makeatother
\fi % end of the ifxeorlua

    \immediate\write\jsonfile{\@charrb} % end the JSON dict

    \closeout\jsonfile
}

\makeatother
% Due to parsing problems with Overleaf's checking for balance of
% start and ends of beginning and ending use of "otherlanguage" and
% because babel and polyglossia & biblatex use different names for Norsk and German
% the following new commands have been added

\ifxeorlua
    \newcommand{\babelpolyLangStop}[1]{\end{#1}}
\else
    \newcommand{\babelpolyLangStop}[1]{\end{otherlanguage}}
\fi

\ifxeorlua
   \newcommand{\babelpolyLangStart}[1]{\begin{#1}}
\else
    \newcommand{\babelpolyLangStart}[1]{\begin{otherlanguage}{#1}}
\fi

\ExplSyntaxOn
% Note that this function returns the _string_ stored in the scontents buffer
\cs_new:Npn \qgetstored #1 #2
{
\__scontents_getfrom_seq:nn {#1} {#2}
}

\newcommand\typestoredx[2]{\expandafter\__scontents_typestored_internal:nn\expandafter{#1} {#2}}
\ExplSyntaxOff

% for new KTH cover
% Load the Arial font as it is used for the KTH covers
% 
\ifluatex
\newfontfamily\coverlfont[Ligatures=TeX]{Arial}
    
\newfontfamily\coverbfont[Ligatures=TeX]{Arial Bold}
\else
\ifxetex
\newfontfamily\coverlfont[Mapping=tex-text]{Arial}
    
\newfontfamily\coverbfont[Mapping=tex-text]{Arial Bold}
%\newfontfamily\coversbfont[Mapping=tex-text]{Arial Medium}
\else
\newcommand\coverlfont{\fontfamily{helvet}\selectfont\sffamily}
\newcommand\coverbfont{\fontfamily{helvet}\selectfont\sffamily\bfseries}
\fi
\fi


\makeatletter
% For information about the page layout see https://www.overleaf.com/learn/latex/Page_size_and_margins
\newcommand{\kthcover}{
% Note that the values have only been adjusted for A4 paper!
\newgeometry{top=232.34pt,bottom=70.9pt,left=70.9pt, right=70.9pt}

\thispagestyle{empty}



\begin{textblock*}{106.16898110pt}(226.77pt, 35.4pt) % formerly 20pt, 40pt
\includegraphics[width=106.16898110pt, height=118.9419140pt, keepaspectratio]{KTH_logo_RGB_bla.png}
\end{textblock*}
%\vspace{160pt}
\begin{center}
% look for a second subject
\ifx\@secondSubjectArea\@empty

  \ifinswedish
  {\fontsize{12}{13} \coverlfont 
  Examensarbete inom \@subjectArea\\
  }
  \addvspace{8pt}
    {\fontsize{10}{12}  \coverlfont
  \IfEqCase{\@courseCycle}{%
    {1}{Grundnivå,}%
    {2}{Avancerad nivå,}%
  }[\typeout{unknown cycle}]
~\IfEqCase{\@courseCredits}{%
    {5.0}{5}%
    {7.5}{7,5}%
    {10.0}{10}%
    {12.0}{12}%
    {14.0}{14}%
    {15.0}{15}%
    {16.0}{16}%
    {18.0}{18}%
    {20.0}{20}%
    {22.5}{22,5}%
    {28.0}{28}%
    {30.0}{30}%
    {35.0}{33}%
    {37.5}{37,5}%
    {45.0}{45}%
    {60.0}{60}%
    {90.0}{90}%
    {120.0}{120}%
    {180.0}{180}%
    {210.0}{210}%
    {240.0}{240}%
    {300.0}{300}%
    {330.0}{330}%
    }[\typeout{unknown credits}]%
~hp\\
    }
  \else
{\coverlfont \fontsize{12}{13}
  Degree Project in \@subjectArea\\
}
  \vspace{8pt}
  {\fontsize{10}{12} \coverlfont 
  \IfEqCase{\@courseCycle}{%
    {1}{First cycle,}%
    {2}{Second cycle,}%
  }[\typeout{unknown cycle}]
\,\IfEqCase{\@courseCredits}{%
    {5.0}{5}%
    {7.5}{7.5}%
    {10.0}{10}%
    {12.0}{12}%
    {14.0}{14}%
    {15.0}{15}%
    {16.0}{16}%
    {18.0}{18}%
    {20.0}{20}%
    {22.5}{22.5}%
    {28.0}{28}%
    {30.0}{30}%
    {35.0}{33}%
    {37.5}{37.5}%
    {45.0}{45}%
    {60.0}{60}%
    {90.0}{90}%
    {120.0}{120}%
    {180.0}{180}%
    {210.0}{210}%
    {240.0}{240}%
    {300.0}{300}%
    {330.0}{330}%
    }[\typeout{unknown credits}]%
~credits\\
  }
  \fi
    
\else
  \ifinswedish
  {\fontsize{12}{13} \coverlfont 
      \ifthenelse{\equal{\@subjectArea}{\@secondSubjectArea}}
    {Examensarbete inom teknikområdet och huvudområdet \@subjectArea\\}
    {Examensarbete inom teknikområdet \@subjectArea\ och huvudområdet \@secondSubjectArea\\}%
  }
%  \IfEqCase{\@degreeName}{%
%    {Both}{Examensarbete inom teknikområdet \@subjectArea\ och huvudområdet \@secondSubjectArea\\}%
%    {Same}{Examensarbete inom teknikområdet och huvudområdet \@subjectArea\\}%
%  }[\typeout{unknown degree name in case for both Masters degrees}]
  \vspace{8pt}
   {\fontsize{10}{12} \coverlfont
  \IfEqCase{\@courseCycle}{%
    {1}{Grundnivå,}%
    {2}{Avancerad nivå,}%
  }[\typeout{unknown cycle}]
~\IfEqCase{\@courseCredits}{%
    {15.0}{15}%
    {30.0}{30}%
    }[\typeout{unknown credits}]%
~hp\\
    }
  \else
  {\fontsize{12}{13} \coverlfont
  \ifthenelse{\equal{\@subjectArea}{\@secondSubjectArea}}
    {Degree Project in the Field of Technology and the Main Field of Study \@subjectArea\\}
    {Degree Project in the Field of Technology \@subjectArea\ and the Main Field of Study \@secondSubjectArea\\}%
  }
%    \IfEqCase{\@degreeName}{%
%    {Both}{Degree Project in the Field of Technology \@subjectArea\ and the Main Field of Study \@secondSubjectArea\\}%
%    {Same}{Degree Project in the Field of Technology and the Main Field of Study \@subjectArea\\}%
%  }[\typeout{unknown degree name in case for both Masters degrees}]
  
  \vspace{8pt}
  {\fontsize{10}{12} \coverlfont
  \IfEqCase{\@courseCycle}{%
    {1}{First cycle,}%
    {2}{Second cycle,}%
  }[\typeout{unknown cycle}]
\,\IfEqCase{\@courseCredits}{%
    {15.0}{15}%
    {30.0}{30}%
    }[\typeout{unknown credits}]%
~credits\\
  }
  \fi

\fi
\addvspace{28pt}
{\fontsize{26}{30}\coverbfont \@title \par }


\ifx\@subtitle\@empty\relax
\else
\vspace{12pt}
    {\fontsize{16}{18}\coverlfont  \@subtitle \par }
\fi

\vspace{30pt}
    {\fontsize{12}{13}\coverbfont
    \expandafter\MakeUppercase\expandafter\@authorsFirstname\space\expandafter\MakeUppercase\expandafter\@authorsLastname \par
    \ifx\@secondAuthorsLastname\@empty\relax
    \else\addvspace{2pt}\expandafter\MakeUppercase\expandafter\@secondAuthorsFirstname\space\expandafter\MakeUppercase\expandafter\@secondAuthorsLastname \par
    \fi
    }
\end{center}
\vfill

\restoregeometry
\clearpage
}

\newcommand{\kthbackcover}{
% Note that the values have only been adjusted for A4 paper!
\newgeometry{top=232.34pt,bottom=70.9pt,left=70.9pt, right=70.9pt}

\thispagestyle{empty}

% Generate the back cover with the TRITA number and the fixed graphical elements
\begin{textblock*}{5cm}(38.83pt, 740.89pt) % {block width} (coords) - 297mm - 101pt
\noindent{\fontsize{10}{12}\coverlfont 
    \ifx\@thesisSeries\@empty %\relax
        TRITA xxxx:yyy
        \else
        	\@thesisSeries\,\ifx\@thesisSeriesNumber\@empty\relax
            \else
            \@thesisSeriesNumber
             \fi
    \fi\\
}
\end{textblock*}
\begin{textblock*}{510pt}(38.83pt, 751.89pt ) % {block width} (coords) - {297mm - 90pt}
\ifinswedish
\noindent{\fontsize{8}{10}\coverlfont Stockholm, Sverige \the\year{}}\\
  \else
\noindent{\fontsize{8}{10}\coverlfont Stockholm, Sweden \the\year{}}\\
  \fi
\end{textblock*}
\begin{textblock*}{5cm}(38.83pt, 778.89pt) % {block width} (coords)  - was 44pt - {297mm - 63pt}
\noindent{\fontsize{8}{9}\coverlfont
    \textcolor{kth-blue}{www.kth.se}
}
\end{textblock*}

\restoregeometry
\null\newpage
}

% Command to print out the standardized title page
\renewcommand{\titlepage}{
  \newgeometry{top=65mm,bottom=30mm,left=74pt,right=35mm} % formerly left=50mm

\thispagestyle{empty}


\begin{huge}
  \begin{flushleft}
    \noindent\sffamily\bfseries \@title \par
  \end{flushleft}
\end{huge}

\ifx\@subtitle\@empty\relax
\else
\begin{Large}
  \vspace{1ex}
  \begin{flushleft}
    \noindent\sffamily\bfseries \@subtitle \par
  \end{flushleft}
\end{Large}
\fi


\vspace{10mm}
\begin{large}
  \begin{flushleft}
    \sffamily
    \expandafter\MakeUppercase\expandafter\@authorsFirstname\space\expandafter\MakeUppercase\expandafter\@authorsLastname \par
    \ifx\@secondAuthorsLastname\@empty\relax
    \else\vspace{1ex}\expandafter\MakeUppercase\expandafter\@secondAuthorsFirstname\space\expandafter\MakeUppercase\expandafter\@secondAuthorsLastname \par
    \fi
  \end{flushleft}
\end{large}

\vfill

\begin{flushleft}
  \sffamily
  \ifinswedish
%    \programmecode{\@programcode}\par
%    \ifx\@secondProgramcode och \programmecode{\@secondProgramcode} \par \fi  % for a second program
    \@prgmcode\par
    \ifx\@prgmcode och \@secondprgmcode \par  \fi   % for a second program
    \ifx\@date\@empty\relax\else Datum: \@date\\ \vspace{5mm} \fi
    \ifx\@supervisorCsLastname\@empty
    \ifx\@supervisorBsLastname\@empty
    Handledare: \@supervisorAsFirstname\space\@supervisorAsLastname
        \else
    Handledare: \@supervisorAsFirstname\space\@supervisorAsLastname,  \@supervisorBsFirstname\space\@supervisorBsLastname
        \fi
    \else
        Handledare: \@supervisorAsFirstname\space\@supervisorAsLastname,  \@supervisorBsFirstname\space\@supervisorBsLastname,
            \@supervisorCsFirstname\space\@supervisorCsLastname
    \par
    \fi
    Examinator: \@examinersFirstname\space\@examinersLastname\par
    \quad\@examinersSchool\par
    \ifx\@hostcompany\@empty\relax\else Uppdragsgivare: \@hostcompany \par \fi
    \ifx\@hostorganization\@empty\relax\else Uppdragsgivare: \@hostorganization \par \fi
    \ifx\@alttitle\empty\relax\else Engelsk titel: %
    \sffamily\@alttitle \fi
    \ifx\@altsubtitle\@empty\relax
    \else
    English subtitle \sffamily\@altsubtitle \\
    \fi
  \else
    \@prgmcode\par
    \ifx\@prgmcode och \@secondprgmcode \par  \fi   % for a second program
    \ifx\@date\@empty\relax\else Date: \@date\\ \vspace{5mm} \fi
    
    \ifx\@supervisorCsLastname\@empty
        \ifx\@supervisorBsLastname\@empty
    Supervisor: \@supervisorAsFirstname\space\@supervisorAsLastname
        \else
    Supervisors: \@supervisorAsFirstname\space\@supervisorAsLastname,  \@supervisorBsFirstname\space\@supervisorBsLastname
        \fi
    \else
        Supervisors: \@supervisorAsFirstname\space\@supervisorAsLastname,  \@supervisorBsFirstname\space\@supervisorBsLastname,
            \@supervisorCsFirstname\space\@supervisorCsLastname
    \par
    \fi

    Examiner: \@examinersFirstname\space\@examinersLastname\par
    \quad\@examinersSchool\par
    \ifx\@hostcompany\@empty\relax\else Host company: \@hostcompany \par \fi
    \ifx\@hostorganization\@empty\relax\else Host organization: \@hostorganization \par \fi
    \ifx\@alttitle\empty\relax\else Swedish title: %
        \sffamily\@alttitle  \par \fi
    \ifx\@altsubtitle\@empty\relax \else Swedish subtitle: %
        \sffamily\@altsubtitle \par \fi
  \fi
\end{flushleft}
\restoregeometry
\clearpage
}

% Command to print out the standardized document information page
\newcommand{\bookinfopage}{
  \newgeometry{top=250mm,bottom=30mm,left=74pt,right=35mm}
\thispagestyle{empty}
\begin{flushleft}
  \sffamily
  \copyright\enspace\the\year\quad\@authorsFirstname\space\@authorsLastname 
  \ifx\@secondAuthorsLastname\@empty\relax
  \else
    \ifinswedish
      \enspace och\enspace\@secondAuthorsFirstname\space\@secondAuthorsLastname \\
    \else
      \enspace and\enspace\@secondAuthorsFirstname\space\@secondAuthorsLastname \\
    \fi
  \fi
\end{flushleft}
\restoregeometry
\clearpage
}
\makeatother

\endinput
%% End of file `timtm.cls'.
