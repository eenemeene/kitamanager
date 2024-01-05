async function child_contract_count_group_by_area(historydate) {

    let c = document.getElementById("childContractCountGroupByAreaChart");
    let ctx = c.getContext("2d");
    let childContractCountGroupByAreaChart = new Chart(ctx, {
        type: "pie",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });
    let url = '{% url "kitamanager:child-charts-count-group-by-area" %}?historydate=' + historydate
    await loadChart(childContractCountGroupByAreaChart, url)
}

