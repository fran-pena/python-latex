from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode
import tex_to_python  
def extract_text_from_node(node):
    """Extrae todo el texto de un nodo y sus subnodos recursivamente"""
    if hasattr(node, 'chars'):
        return node.chars
    elif hasattr(node, 'nodelist'):
        # Para nodos que contienen otros nodos (grupos, entornos, etc.)
        text_parts = []
        for subnode in node.nodelist:
            text_parts.append(extract_text_from_node(subnode))
        return ''.join(text_parts)
    elif hasattr(node, 'latex_verbatim'):
        # Para nodos que tienen método latex_verbatim
        return node.latex_verbatim()
    else:
        return ""
    
w = LatexWalker(r"""
    \begin{algorithmic}
    \State $i = 10$
    \If{$i\geq 5$} 
        \State $i = i-1$
    \Else
        \If{$i\leq 3$}
            \State $i = i+2$
        \EndIf
    \EndIf 
    \end{algorithmic}
    """)

w = LatexWalker(r"""
    \begin{equation}
        f(x) = x^3-\ln(x)-3
        \label{eq:calc:f}
    \end{equation}
    \begin{equation}
        a = 1
        \label{eq:calc:a}
    \end{equation}
""")

(nodelist, pos, len_) = w.get_latex_nodes(pos=0)
print(nodelist[1].nodelist[3])




