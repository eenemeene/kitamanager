async function bankaccount_sum_balance_by_month(historydate) {

    let c = document.getElementById("bankAccountSumBalanceByMonthChart");
    let ctx = c.getContext("2d");
    let bankAccountSumBalanceByMonthChart = new Chart(ctx, {
        type: "bar",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });
    let url = '{% url "kitamanager:bankaccount-charts-sum-balance-by-month" %}?historydate=' + historydate
    await loadChart(bankAccountSumBalanceByMonthChart, url)
}
