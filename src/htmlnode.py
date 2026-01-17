class HTMLNode():
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()
    
    def props_to_html(self):
        output = ""
        if self.props == None:
            return output
        for prop in self.props:
            output += f" {prop}=\"{self.props[prop]}\""
        return output
    
    def __repr__(self):
        children = ""
        props = ""
        if self.children != None:
            for child in self.children:
                children += f"{child.__repr__()},"
        if self.props != None:
            for prop in self.props:
                props += f"key= {prop}, value= {self.props[prop]},"
        return f"HTMLNode(tag= {self.tag}, value= {self.value}, children= {children}, props= {props})"
    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
        self.tag = tag
        self.value = value
        self.props = props

    def to_html(self):
        if self.value == None:
            raise ValueError()
        if self.tag == None:
            return self.value
        else:
            return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
        
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
        self.tag = tag
        self.children = children
        self.props = props

    def to_html(self):
        if self.tag == None:
            raise ValueError("Tag is missing")
        if self.children == None:
            raise ValueError("No children found")
        output = f"<{self.tag}{self.props_to_html()}>"
        for child in self.children:
            output += child.to_html()
        output += f"</{self.tag}>"
        return output

    