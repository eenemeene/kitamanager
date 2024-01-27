async function statistic_child_requirements_vs_employee_hours(historydate) {

    let c = document.getElementById("statisticChildRequirementVsEmployeeHoursChart");
    let ctx = c.getContext("2d");
    let statisticChildRequirementVsEmployeeHoursChart = new Chart(ctx, {
        type: "bar",
        options: {
            title: {
                display: false,
                text: ""
            },
        }
    });
    let url = '{% url "kitamanager:statistic-charts-child-requirement-vs-employee-hours" %}?historydate=' + historydate
    await loadChart(statisticChildRequirementVsEmployeeHoursChart, url)
}

