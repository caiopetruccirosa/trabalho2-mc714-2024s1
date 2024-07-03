import os
import logging

from node import Node
from typing import List, Tuple, Dict


def _get_nodes_info(raw_nodes_info: str):
    """
    Parse the raw nodes info string into a dictionary of node id and host.
    The raw nodes info string is in the format "id1::host1,id2::host2,...,idn::hostn".
    """
    unparsed_nodes_info: List[Tuple[str]] = [ tuple(node_info.split('::', maxsplit=1)) for node_info in raw_nodes_info.split(",") ]
    parsed_nodes_info: Dict[int, str] = { int(id_str): host for id_str, host in unparsed_nodes_info }
    return parsed_nodes_info


if __name__ == "__main__":
    node_id = int(os.environ.get("NODE_ID"))
    node_port = os.environ.get("NODE_PORT")
    other_nodes = _get_nodes_info(os.environ.get("OTHER_NODES"))

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(f"Node {node_id}")

    node = Node(
        node_id=node_id,
        node_port=node_port, 
        other_nodes=other_nodes, 
        logger=logger,
    )
    node.run_node()
