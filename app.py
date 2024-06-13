import requests
import streamlit as st

st.set_page_config(page_title="Context diff", page_icon="🧊", layout="wide")


def fetch_available_repos():
    url = "https://sscontext-m32vxc65wa-uc.a.run.app/sscontext.v1.SSContextService/ListIndexingOperations"
    r = requests.post(url, json={}, headers={"Accept": "application/json"})
    return dict((o["repoName"], o["operationId"]) for o in r.json()["operations"])


def fetch_context(operation_id, query):
    url = "https://sscontext-m32vxc65wa-uc.a.run.app/sscontext.v1.SSContextService/ComputeContext"
    r = requests.post(
        url,
        json={"indexingOperationId": operation_id, "query": query},
        headers={"Accept": "application/json"},
    )
    return r.json()


with st.spinner("Fetching context..."):
    repos_to_ops = fetch_available_repos()


def format_context_item(i):
    return "{}#{}-{}".format(
        i["fileName"], i.get("lineFrom", 0), i["lineTo"], i["indexerScore"]
    )


with st.form("query"):
    query = st.text_input(
        "query", placeholder="Where is pool defined?", value="Where is pool defined?"
    )
    repo = st.selectbox("Repo", repos_to_ops.keys())
    if st.form_submit_button("Fetch context"):
        with st.spinner("Fetching context..."):
            st.session_state.ctx = fetch_context(repos_to_ops[repo], query)

if "ctx" in st.session_state:
    emb, met = [], []
    for i in st.session_state.ctx["contextItems"]:
        if i["indexer"] == "INDEXER_EMBEDDINGS":
            emb.append(i)
        else:
            met.append(i)
    left_column, right_column = st.columns(2)
    with left_column:
        option = st.selectbox(
            "embeddings",
            emb,
            format_func=format_context_item,
            index=0,
        )
        print(format_context_item(option))
        for i in emb:
            if format_context_item(i) == format_context_item(option):
                c = st.code(i["content"])
                left_column.write("Indexer score: {}".format(i["indexerScore"]))
    with right_column:
        option = st.selectbox(
            "metadata",
            met,
            format_func=format_context_item,
            index=0,
        )
        for i in met:
            if format_context_item(i) == format_context_item(option):
                st.code(i["content"])
                right_column.write("Indexer score: {}".format(i["indexerScore"]))
