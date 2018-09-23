from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective
from sphinx import addnodes
from docutils import nodes
from sphinx.transforms import SphinxTransform
from sphinx.writers.html5 import HTML5Translator


class HTML5VerbosityTranslator(HTML5Translator):
    def starttag(self, node, tagname, suffix='\n', empty=False, **attributes):
        if tagname in ['div', 'p', 'span', 'a']:
            if int(node.get('verbosity', 1)) > 1:
                attributes['data-verbosity'] = node['verbosity']
                attributes['hidden'] = "true"

        return super().starttag(
            node, tagname, suffix=suffix, empty=empty, **attributes)

    # def visit_literal_block(self, node):
    #     self.body.append(f"<div data-verbosity={node.get('verbosity', 1)}>\n")
    #     super().visit_literal_block(node)

    # def depart_literal_block(self, node):
    #     super().depart_literal_block(node)
    #     self.body.append(f"\n<\div>")


slider_instance = """
<form class="slidecontainer">
    Verbosity level :
    <input type="range" min="1" max="3" value="1" name="verbositySlider" id="verbosity_slider" onchange="changeVerbosity(this.value);">
    <input type="number" maxlength="1" id="verbosity_value" min="1" max="3" value="1" oninput="changeVerbosity(this.value);" />
</form>
"""
slider_onchange = """
<script>
 function changeVerbosity(verbosity) {

     document.getElementById("verbosity_value").value = verbosity;
     document.getElementById("verbosity_slider").value = verbosity;

     var a = document.querySelectorAll('[data-verbosity]');

     for (var i in a) if (a.hasOwnProperty(i)) {
         if (a[i].getAttribute('data-verbosity') <= verbosity) {
             a[i].removeAttribute("hidden")
         } else {
             a[i].setAttribute("hidden", "true")
         }
     }
 }
</script>
"""


class verbosity(nodes.Element):
    """Inserted to set the highlight language and line number options for
    subsequent code blocks.
    """


class Verbosity(SphinxDirective):
    """
    Directive to set the highlighting language for code blocks, as well
    as the threshold for line numbers.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    # option_spec = {
    #     'linenothreshold': directives.positive_int,
    # }

    def run(self):
        # type: () -> List[nodes.Node]
        # linenothreshold = self.options.get('linenothreshold', sys.maxsize)
        return [verbosity(verbosity=self.arguments[0].strip())]


class verbosity_slider(nodes.Element):
    """Inserted to set the highlight language and line number options for
    subsequent code blocks.
    """


class verbosity_span(nodes.Element):
    """Inserted to set the highlight language and line number options for
    subsequent code blocks.
    """


class VerbositySlider(SphinxDirective):
    """
    Directive to set the highlighting language for code blocks, as well
    as the threshold for line numbers.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    # option_spec = {
    #     'linenothreshold': directives.positive_int,
    # }

    def run(self):
        # type: () -> List[nodes.Node]
        return [verbosity_slider()]


class VerbosityTransform(SphinxTransform):
    """
    Apply highlight_language to all literal_block nodes.

    This refers both :confval:`highlight_language` setting and
    :rst:dir:`highlightlang` directive.  After processing, this transform
    removes ``highlightlang`` node from doctree.
    """
    default_priority = 400

    def apply(self):
        visitor = VerbosityVisitor(self.document)
        self.document.walkabout(visitor)

        for node in self.document.traverse(verbosity):
            node.parent.remove(node)


class VerbosityVisitor(nodes.NodeVisitor):
    def __init__(self, document):
        # type: (nodes.document, unicode) -> None
        self.default_setting = 1
        self.settings = []  # type: List[HighlightSetting]
        nodes.NodeVisitor.__init__(self, document)

    def unknown_visit(self, node):
        # type: (nodes.Node) -> None
        pass

    def unknown_departure(self, node):
        # type: (nodes.Node) -> None
        pass

    def visit_document(self, node):
        # type: (nodes.Node) -> None
        self.settings.append(self.default_setting)

    def depart_document(self, node):
        # type: (nodes.Node) -> None
        self.settings.pop()

    def visit_start_of_file(self, node):
        # type: (nodes.Node) -> None
        self.settings.append(self.default_setting)

    def depart_start_of_file(self, node):
        # type: (nodes.Node) -> None
        self.settings.pop()

    def visit_verbosity(self, node):
        # type: (addnodes.highlightlang) -> None
        prev_setting = self.settings[-1]
        self.settings[-1] = node['verbosity']
        parent = node.parent

        # import pdb
        # pdb.set_trace()

        if parent.index(node) == 0:
            # node_rec = node
            # while node_rec and node_rec.parent.index(node_rec) == 0:
            # node_rec.parent['verbosity'] = node['verbosity']
            # node_rec = node_rec.parent
            node.parent['verbosity'] = node['verbosity']
            node = node.parent

        else:
            node_i = parent.index(node)
            if 'verbosity' in parent:
                del parent['verbosity']
                for c in (parent.children[:node_i]):
                    if isinstance(c, nodes.Text):
                        subs = verbosity_span('', c, verbosity=prev_setting)
                        parent.replace(c, subs)
                    else:
                        c['verbosity'] = prev_setting

            for c in parent.children[node_i + 1:]:
                if isinstance(c, verbosity):
                    break
                elif isinstance(c, nodes.Text):
                    subs = verbosity_span('', c, verbosity=node['verbosity'])
                    parent.replace(c, subs)
                else:
                    c['verbosity'] = node['verbosity']


def visit_verbosity_span(self, node):
    self.body.append(self.starttag(node, 'span', ''))


def depart_verbosity_span(self, node):
    self.body.append('</span>')


def visit_verbosity(self, node):
    pass


def depart_verbosity(self, node):
    pass


def visit_verbosity_slider(self, node):
    self.body.append(slider_onchange)
    self.body.append(slider_instance)


def depart_verbosity_slider(self, node):
    pass


def verbosity_role(name,
                   rawtext,
                   text,
                   lineno,
                   inliner,
                   options={},
                   content=[]):
    return [verbosity(verbosity=text)], []


def setup(app):
    app.add_node(verbosity, html=(visit_verbosity, depart_verbosity))
    app.add_node(
        verbosity_slider,
        html=(visit_verbosity_slider, depart_verbosity_slider))
    app.add_node(
        verbosity_span, html=(visit_verbosity_span, depart_verbosity_span))

    app.add_directive('verbosity', Verbosity)
    app.add_directive('verbosity_slider', VerbositySlider)
    app.add_role('v', verbosity_role)

    app.add_post_transform(VerbosityTransform)
    app.set_translator('html', HTML5VerbosityTranslator)
