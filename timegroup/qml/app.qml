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
            width: Math.min(parent.width - 40, 400)
            spacing: 24

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: qsTr("TimeGroup Reporter")
                font.pixelSize: 28
                font.bold: true
                color: "#4f46e5"
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 16
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

                TextField {
                    id: spreadsheetUrlInput
                    Layout.fillWidth: true
                    placeholderText: qsTr("Nhập URL Google Spreadsheet URL")
                    font.pixelSize: 14
                    color: "#374151"
                    background: Rectangle {
                        implicitWidth: 200
                        implicitHeight: 40
                        color: "white"
                        border.color: spreadsheetUrlInput.focus ? "#4f46e5" : "#d1d5db"
                        radius: 4
                    }
                }

                Button {
                    id: exportButton
                    Layout.fillWidth: true
                    text: qsTr("Cập nhật báo cáo")
                    font.pixelSize: 16
                    font.bold: true
                    Material.background: Material.accent
                    Material.foreground: "white"
                    enabled: reportModel.isExporting === false

                    contentItem: Item {
                        implicitWidth: rowLayout.implicitWidth
                        implicitHeight: rowLayout.implicitHeight

                        RowLayout {
                            id: rowLayout
                            spacing: 8
                            anchors.centerIn: parent

                            Image {
                                source: "qrc:/resources/icons/export.svg"
                                Layout.preferredWidth: 20
                                Layout.preferredHeight: 20
                            }
                            Text {
                                text: exportButton.text
                                color: exportButton.Material.foreground
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            var timeFrame = timeFrameCombo.model[timeFrameCombo.currentIndex]

                            var reportType = ""
                            if (reportTypeCombo.currentIndex === 0) {
                                reportType = "order"
                            } else if (reportTypeCombo.currentIndex === 1) {
                                reportType = "revenue"
                            } else {

                            }

                            if (timeFrameCombo.currentIndex === 0) {
                                timeFrame = "yesterday"
                            } else if (timeFrameCombo.currentIndex === 1) {
                                timeFrame = "last_month"
                            } else if (timeFrameCombo.currentIndex === 2) {
                                timeFrame = "last_month_and_current_month"
                            }
                            reportModel.exportReport(reportType, timeFrame)
                        }
                    }
                }

                Text {
                    text: qsTr(reportModel.messageInfo)
                    color: "#4f46e5"
                }
            }
        }
    }


    Component.onCompleted: {
        x = (Screen.width - width) / 2
        y = (Screen.height - height) / 2
    }

}
