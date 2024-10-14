import os
import polars as pl
from logging import getLogger
from attack_predictor_libs.mitre.mitre import get_parent_technique, get_technique_phase, get_technique_tactic, is_preparation_technique, is_compromise_technique, is_intrusion_technique, get_technique_name
import networkx as nx
from networkx.drawing import nx_agraph
from plotly import graph_objs as go
import numpy as np

logger = getLogger(__name__)

def visualize_scenario(scenariodataset: pl.DataFrame, drop_subtechnique: bool = True, outputfileName: str | None = None) -> None:
    """シナリオデータを可視化する。

    Args:
        scenariodataset (pl.DataFrame): シナリオデータ(GUIDEデータセットフォーマット)。

        display_subtechnique (bool): サブテクニックを表示するかどうか
    """
    if (outputfileName is not None) and os.path.exists(outputfileName):
        raise FileExistsError(f"File already exists: {outputfileName}")

    
    
    scenariodataset.sort("Timestamp")
    logger.debug("Timestampでソートした。")

    
    
    technique_list = scenariodataset.get_column("MitreTechniques").to_list()
    
    
    G = create_networkx_instance(technique_list, drop_subtechnique=drop_subtechnique)
    print(G)

    technique_name_dict = { node:get_technique_name(node) for node in G.nodes() if node != "START" and node != "END"}
    technique_name_dict["START"] = "START"
    technique_name_dict["END"] = "END"

    technique_hovermessage_dict =  {node:_get_hover_message(node) for node in G.nodes() if node != "START" and node != "END"}
    technique_hovermessage_dict["START"] = None
    technique_hovermessage_dict["END"] = None

    technique_phase_number_dict = { node: get_technique_phase(node) for node in G.nodes() if node != "START" and node != "END"}
    technique_phase_number_dict["START"] = "START"
    technique_phase_number_dict["END"] = "END"

    
    pos = nx_agraph.graphviz_layout(
        G,
        prog='neato',
        args='-Goverlap="scalexy" -Gsep="+6" -Gnodesep=0.8 -Gsplines="polyline" -GpackMode="graph" -Gstart={}'.format(0)
    )
    
    _build_interactive_network(G, pos, node_text_dict=technique_name_dict, nodehovertext_dict=technique_hovermessage_dict, node_colors_dict=technique_phase_number_dict, outputfile=outputfileName)




    
    
def _build_interactive_network(G, pos, node_text_dict: dict[str, str] | None = None, nodehovertext_dict: dict[str, str] | None = None, node_colors_dict: list[str, str] = None, outputfile: str | None = None):
    # edgeデータの作成
    edge_x = []
    edge_y = []
    arrow_x = []
    arrow_y = []
    arrow_pos_ratio = 0.8

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        
        edge_y.append(y0)
        edge_y.append(y1)
        
        vex_x = x0 * (1-arrow_pos_ratio) + x1 * arrow_pos_ratio
        vex_y = y0 * (1-arrow_pos_ratio) + y1 * arrow_pos_ratio
                # 終点より手前に矢印を表示するため、ベクトルの長さに応じてオフセットする
        
        length = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        
        if abs(length) <= 0.0001:
            continue
        arrow_x.append(vex_x)
        arrow_y.append(vex_y)
        

        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.0, color='#888'),
        mode='lines',
        hoverinfo='none'
    )

    arrow_trace = go.Scatter(
        x=arrow_x,
        y=arrow_y,
        mode='markers',
        marker=dict(
            size=10,  # 矢印のサイズ
            symbol='triangle-up',  # 矢印として三角形を使用
            angleref='previous',  # 矢印の向きはエッジに沿う
            color='black'  # 矢印の色
        ),
        hoverinfo='none'
    )
    
    
    
    
    # nodeデータの作成
    node_x = []
    node_y = []
    nodehovertext_list = []
    node_name_list = []
    node_color_list = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_name_list.append(node_text_dict[node])
        nodehovertext_list.append(nodehovertext_dict[node])
        node_color_list.append(node_colors_dict[node])


    color_map = {
        "START": "gray",
        "END": "gray",
        "Preparation": 'yellow',
        "Intrusion": 'orange',
        "Compromise": 'red'
    }
    default = "gray"
    mapped_colors = [color_map.get(color, default) for color in node_color_list]  # 設定されていない色は絶対色(例: 'grey')    
 
    # nodeの色、サイズ、マウスオーバーしたときに表示するテキストの設定
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        text=node_name_list,
        hovertext=nodehovertext_list,
        textposition='top center',
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='Portland',
            reversescale=False,
            color=mapped_colors,
            size=[15]*len(G.nodes()),
            line_width=2
        ),
    )
    

    
    data = [edge_trace, node_trace, arrow_trace]  
    # data = [edge_trace, node_trace]  
    # data = [node_trace]  + arrow_trace

    # レイアウトの設定
    layout=go.Layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=10, l=5, r=5, t=10),
                font=dict(size=10),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,scaleanchor="y", scaleratio=1),
                yaxis = dict(showgrid = False, zeroline = False, showticklabels = False, scaleanchor="x", scaleratio=1))

    fig = go.Figure(data=data, layout=layout)    
    
    if outputfile is None:
        fig.show()
    else:
        if os.path.exists(outputfile):
            os.remove(outputfile)
        fig.write_html(outputfile)
    





EDGE = tuple[str, str]
def create_networkx_instance(technique_list: list[str], drop_subtechnique: bool = True) -> nx.Graph:
    
    
    
    edge_list = create_edge_from_technique_list(technique_list, drop_subtechnique=drop_subtechnique)
    
    G = nx.Graph()

    ## add node
    G.add_node("START")
    G.add_node("END")

    first_technique_set = set([  tech_id for tech_id in unwrap_delimiter(technique_list[0])])
    last_technique_set = set([  tech_id for tech_id in unwrap_delimiter(technique_list[-1])])
    
    if drop_subtechnique:
        first_technique_set = set([ get_parent_technique(tech_id) for tech_id in first_technique_set])
        last_technique_set = set([ get_parent_technique(tech_id) for tech_id in last_technique_set])


    for tech in first_technique_set:
        G.add_edge("START", tech)

    for tech in last_technique_set:
        G.add_edge(tech, "END")

    G.add_edges_from(edge_list)

    return G


    
def _get_hover_message(technique_id: str) -> str:
    phase = get_technique_phase(technique_id)
    tactic = get_technique_tactic(technique_id)
    technique = get_technique_name(technique_id)
    is_pre = is_preparation_technique(technique_id)
    is_com = is_compromise_technique(technique_id)
    is_int = is_intrusion_technique(technique_id)

    
    return (
        f"phase: {phase}, phasenum: {int(is_pre)} {int(is_int)} {int(is_com)}<br>"
        f"tactic: {tactic}<br>"
        f"Technique: f{technique}({technique_id})"
    )
    





def create_edge_from_technique_list(technique_ids_list : list[str], drop_subtechnique: bool = True) -> set[str, str]:
    """_summary_

    Args:
        technique_list (list[str]): 
            当該シナリオで実行されたMITRE Techniqueリスト。時系列でソートされている。
            実行したTechniqueが一つに決められない場合は、';'区切りで書かれている。
    Returns:
        set[str, str]: (source, target)のエッジのリスト。時系列リストデータをグラフ構造に変換している。
    """
    edge_set = set()

    for technique_ids in range(len(technique_ids_list)-1):
        source_list = unwrap_delimiter(technique_ids_list[technique_ids])
        destination_list = unwrap_delimiter(technique_ids_list[technique_ids+1])

        if drop_subtechnique:
            source_list = set([ get_parent_technique(src) for src in source_list])
            destination_list = set([get_parent_technique(dst) for dst in destination_list])
                    
        for src in source_list:
            for dst in destination_list:
                edge = (src, dst)
                edge_set.add(edge)

    return edge_set

def unwrap_delimiter(message: str, delimiter=";") -> list[str]:
    """_summary_

    Args:
        message (str): 
            メッセージ。';'区切りで書かれている。
        delimiter (str, optional): 
            区切り文字。デフォルトは';'。
    Returns:
        list[str]: 区切り文字で分割されたリスト。
    """
    return [ c.strip()  for c in message.split(delimiter)]


    

# def visualize_scenario(scenariodataset: pl.DataFrame, display_subtechnique: bool = False) -> None:
#     """
#     シナリオデータを可視化する。
#     Args:
#         scenariodataset (pl.DataFrame): シナリオデータ
#         display_subtechnique (bool): サブテクニックを表示するかどうか
#     """
#     # シナリオデータの整形
#     scenariodataset = scenariodataset.with_columns(
#         pl.col("MitreTechniques").map_elements(lambda x: x.split(";"), return_dtype=pl.Object).alias("MitreTechniques")
#     )
    
#     # シナリオデータの可視化
#     for i, row in scenariodataset.iterrows():
#         print(f"Scenario ID: {row['IncidentId']}")
#         print(f"Timestamp: {row['Timestamp']}")
#         print(f"Description: {row['Description']}")
#         print(f"Techniques: {row['MitreTechniques']}")
#         print(f"Subtechniques: {row['Subtechniques']}")
#         print(f"Preparation: {row['is_preparation_alert']}")
#         print(f"Intrusion: {row['is_intrusion_alert']}")
#         print(f"Compromise: {row['is_compromise_alert']}")
#         print("--------------------------------------------------")
        
#         if display_subtechnique:
#             for subtechnique in row['Subtechniques']:
#                 print(f"Subtechnique: {subtechnique}")
#             print("--------------------------------------------------")
            
#     return