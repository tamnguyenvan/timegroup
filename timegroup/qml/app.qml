import QtQuick 6.7
import QtQuick.Controls 6.7
import QtQuick.Layouts 6.7
import QtQuick.Controls.Material 6.7

ApplicationWindow {
    id: window
    visible: true
    width: 800
    height: 600
    minimumWidth: width
    minimumHeight: height
    maximumWidth: width
    maximumHeight: height
    title: qsTr("TimeGroup Reporter")
    Material.theme: Material.Light
    Material.accent: "#4f46e5"
    Material.primary: "#4f46e5"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#dbeafe" }
            GradientStop { position: 1.0; color: "#e0e7ff" }
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: Math.min(parent.width - 40, 600)
            spacing: 20

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("TimeGroup Reporter")
                font.pixelSize: 28
                font.bold: true
                color: "#4f46e5"
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: 20
                rowSpacing: 20

                Text {
                    text: qsTr("Loại báo cáo")
                    font.pixelSize: 14
                    color: "#374151"
                }
                ComboBox {
                    id: reportTypeCombo
                    Layout.fillWidth: true
                    model: [qsTr("Báo cáo đơn hàng"), qsTr("Báo cáo lợi nhuận")]
                    font.pixelSize: 14
                    Material.foreground: "#374151"
                    Material.accent: "#4f46e5"
                }

                Text {
                    text: qsTr("Thời gian")
                    font.pixelSize: 14
                    color: "#374151"
                }
                ComboBox {
                    id: timeFrameCombo
                    Layout.fillWidth: true
                    model: [qsTr("Hôm qua"), qsTr("Tháng trước"), qsTr("Tháng trước + Tháng này")]
                    font.pixelSize: 14
                    Material.foreground: "#374151"
                    Material.accent: "#4f46e5"
                }
            }

            // Container for report options
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.max(orderReportOptions.implicitHeight, profitReportOptions.implicitHeight)

                // Checkbox group for order report
                ColumnLayout {
                    id: orderReportOptions
                    anchors.fill: parent
                    spacing: 10
                    visible: reportTypeCombo.currentIndex === 0

                    Text {
                        text: qsTr("Chọn báo cáo:")
                        font.pixelSize: 14
                        color: "#374151"
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 3
                        rowSpacing: 10
                        columnSpacing: 20

                        CheckBox {
                            id: ghtkCheckBox
                            text: qsTr("Đơn hàng ghtk")
                            checked: true
                        }
                        CheckBox {
                            id: vtpCheckBox
                            text: qsTr("Đơn hàng vtp")
                            checked: true
                        }
                        CheckBox {
                            id: inventoryCheckBox
                            text: qsTr("Tồn kho")
                            checked: true
                        }
                        CheckBox {
                            id: waitingCheckBox
                            text: qsTr("Chờ hàng")
                            checked: true
                        }
                        CheckBox {
                            id: posCheckBox
                            text: qsTr("POS")
                            checked: true
                        }
                    }
                }

                // Checkbox group for profit report
                ColumnLayout {
                    id: profitReportOptions
                    anchors.fill: parent
                    spacing: 10
                    visible: reportTypeCombo.currentIndex === 1

                    Text {
                        text: qsTr("Chọn báo cáo:")
                        font.pixelSize: 14
                        color: "#374151"
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        rowSpacing: 10
                        columnSpacing: 20

                        CheckBox {
                            id: profitCheckBox1
                            text: qsTr("Đơn hàng")
                            checked: true
                        }
                        CheckBox {
                            id: profitCheckBox2
                            text: qsTr("Chờ hàng + Tồn kho")
                            checked: true
                        }
                        CheckBox {
                            id: profitCheckBox3
                            text: qsTr("Khu vực")
                            checked: true
                        }
                    }
                }
            }

            // Submit button
            Button {
                id: exportButton
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 200
                text: qsTr("Cập nhật báo cáo")
                font.pixelSize: 16
                font.bold: true
                Material.background: Material.accent
                Material.foreground: "white"
                enabled: !reportModel.isExporting

                contentItem: RowLayout {
                    spacing: 8
                    Image {
                        source: "qrc:/resources/icons/export.svg"
                        Layout.preferredWidth: 20
                        Layout.preferredHeight: 20
                    }
                    Text {
                        text: exportButton.text
                        color: exportButton.Material.foreground
                        font: exportButton.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        Layout.fillWidth: true
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        var timeFrame = timeFrameCombo.model[timeFrameCombo.currentIndex]
                        var reportType = reportTypeCombo.currentIndex === 0 ? "order" : "revenue"

                        if (timeFrameCombo.currentIndex === 0) {
                            timeFrame = "yesterday"
                        } else if (timeFrameCombo.currentIndex === 1) {
                            timeFrame = "last_month"
                        } else if (timeFrameCombo.currentIndex === 2) {
                            timeFrame = "last_month_and_current_month"
                        }

                        var selectedReports = []
                        if (reportType === "order") {
                            if (ghtkCheckBox.checked) selectedReports.push("Đơn hàng ghtk data")
                            if (vtpCheckBox.checked) selectedReports.push("Đơn hàng vtp data")
                            if (inventoryCheckBox.checked) selectedReports.push("TỒN KHO")
                            if (waitingCheckBox.checked) selectedReports.push("CHỜ HÀNG")
                            if (posCheckBox.checked) selectedReports.push("Pos data")
                        } else {
                            if (profitCheckBox1.checked) selectedReports.push("Đơn hàng data")
                            if (profitCheckBox2.checked) selectedReports.push("Chờ hàng + TỒN KHO")
                            if (profitCheckBox3.checked) selectedReports.push("Khu vực data")
                        }

                        reportModel.exportReport(reportType, timeFrame, selectedReports)
                    }
                }
            }

            // Message logs
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: reportModel.messageInfo
                color: "#4f46e5"
                font.pixelSize: 14
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }
        }
    }

    Component.onCompleted: {
        x = (Screen.width - width) / 2
        y = (Screen.height - height) / 2
    }
}