import plotly.express as px
import plotly.graph_objects as go
import blockParser

def visualize_tree(path):
    names, parents = blockParser.add_tree_nodes(path)

    fig = px.treemap(names=names,
                     parents=parents)
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    fig.show()


def visualize_sankey(path):
    labels, source, target, value = blockParser.tree_to_sankey(path)
    title =  path.split('/').pop()
    fig = go.Figure(go.Sankey(
        arrangement='freeform',
        node=dict(
            pad=100,
            thickness=30,
            line=dict(color="black", width=0.5),
            label= labels,
        ),
        link=dict(
            arrowlen=15,
            source=source,  # indices correspond to labels, eg A1, A2, A1, B1, ...
            target=target,
            value=value
        )))

    fig.update_layout(title_text= title, font_size=15)
    fig.show()


def visualize_operations(path, node):
    labels, source, target, value = blockParser.create_sankey_nodes(path, node)
    fig = go.Figure(go.Sankey(
        arrangement='freeform',
        node=dict(
            pad=100,
            thickness=30,
            line=dict(color="black", width=0.5),
            label=labels,

        ),
        link=dict(
            arrowlen=1000,
            source=source,
            target=target,
            value=value
        )))

    fig.update_layout(title_text= node, font_size=15)
    fig.show()
    print(source)
    print(target)
    print(labels)
