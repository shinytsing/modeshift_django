# UI scenario reference

The dashboard smoke path visits `/testing-dashboard/`, verifies the document title and
visible `测试手法展示中心` heading, then verifies that the functional-test total is rendered
from the dashboard status API. This catches route, template, JavaScript, and API integration
regressions without relying on a fixed delay.

The empty-selection guard path clears the default functional/API selections, clicks `执行测试`,
and asserts the exact dialog text. It proves the UI stops an invalid request before it reaches
the test-start API.
