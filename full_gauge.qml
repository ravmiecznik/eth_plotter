import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.4
import QtQuick.Extras 1.4
import QtQuick.Extras.Private 1.0
import QtGraphicalEffects 1.0
import QtCharts 2.0
import QtQuick.Window 2.2
/*
import MGauge 1.0
import MChart 1.0
*/
/*
Window {
    width: 1200
    height: 800
    color: "transparent"
    visible: true
*/
Rectangle{
    id: rect
    objectName: "main_win"
    width: 1200
    height: 800
    color: "transparent"
    property string units: "  kbps"
    property int max_tput: 35
    property string title: "NBIoT UL"
    Image {
            width: rect.width; height: rect.height
            fillMode: Image.PreserveAspectCrop
            source: "resources/background.jpg"
            smooth: true

    }

/*
    Button{
        id: addButton
        width: 100
        height: 20
        text: "Add"
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 10

        onClicked: add()
    }
*/
    Image {
        id: nokia_log
        width: rect.width*0.3; height: rect.height*0.3
        fillMode: Image.PreserveAspectFit
        //horizontalAlignment: Image.AlignLeft
        //verticalAlignment: Image.AlignTop
        source: "resources/nokia-logo-white.png"
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.left: parent.left
        anchors.leftMargin: 200
        Label {
            text: rect.title
            font.pixelSize: rect.height*0.04
            font.bold: true
            style: Text.Outline; styleColor: "black"
            color: "white"
            anchors.top: parent.bottom
            anchors.topMargin: rect.height*0.04
            anchors.left: parent.left
            }
    }

    ChartView {
        id: myChart
        width: rect.width*0.5
        height: rect.height*0.5
        antialiasing: true
        objectName: "chart_view"
        backgroundColor: "transparent"
        theme: ChartView.ChartThemeBlueCerulean
        property int x_old: 0
        property int y_old: 0
        property int x_new: 0
        property int y_new: 0
        property string units: rect.units

        function init_chart(){
            serie.insert(myChart.x_new, myChart.x_new, myChart.y_new)
        }

        function update_chart(){
            serie.replace(myChart.x_old, myChart.y_old, myChart.x_new, myChart.y_new)
        }

        function remove_point(){
            serie.remove(myChart.x_new)
        }

        function overwrite_chart(){
            serie.remove(myChart.x_new)
            serie.insert(myChart.x_new, myChart.x_new, myChart.y_new)
        }

        anchors {
            right: rect.right
            bottom:  rect.bottom
            rightMargin: 50
            bottomMargin: 10

        }
        ValueAxis {
            objectName: "axis"
            id: xAxis
            min: 0
            max: 100
            tickCount: 100
            labelFormat: "%d"
            visible: false
        }
        ValueAxis {
            id: yAxis
            min: 0
            max: rect.max_tput
            tickCount: 5
            labelFormat: "%d"
            titleText: rect.units
            labelsVisible: true

            labelsFont {
                pointSize: myChart.height*0.06
                bold: true
                weight: Font.Black
            }
            titleFont {
                pointSize: 35
                weight: Font.Black
            }
        }
        AreaSeries {
            id: area
            objectName: "yseries"
            //name: "NBIoT UL Traffic"
            axisX: xAxis
            axisY: yAxis
            color: "#00ffff"
            opacity: 0.7
            upperSeries: LineSeries {
                id: serie
            }
       }
    }

    CircularGauge {
        width: rect.width*0.5
        height: rect.height*0.5
        id: gauge
        objectName: "test_gauge"
        property double gauge_value: 0
        property double tick_step : rect.max_tput/30



        anchors {
            left: rect.left
            leftMargin: -100
            bottom:  rect.bottom
            bottomMargin: 40

        }
        Component.onCompleted: forceActiveFocus()
        value: gauge_value
        maximumValue: rect.max_tput  // Largest Value
        minimumValue: 0.0       // Smallest Value

        style: CircularGaugeStyle {
            id: style
            labelStepSize: 2
            labelInset: outerRadius / 7.5
            tickmarkInset: outerRadius / 5.2
            tickmarkStepSize: gauge.tick_step
            minorTickmarkInset: outerRadius / 3.2
            minimumValueAngle: -144
            maximumValueAngle: 144

        background: Rectangle {

            id: bckgr

            implicitHeight: gauge.height*0.8
            implicitWidth: gauge.width*0.8
            opacity: 0.5
            color: "blue"
            anchors.centerIn: parent
            radius: 360
              Glow {
              anchors.fill: picture
              radius: 10
              samples: 10
              color: "#0d315f"
              source: picture
          }
          Image {
                id: picture
                anchors.fill: parent
                source: "resources/background.svg"
                asynchronous: true
                sourceSize {
                    width: width
                    height: height
                }
            }
           }

        foreground: Item {
            Text {
                id: speedLabel
                anchors.centerIn: parent
                text: gauge.value.toFixed(0)
                font.pixelSize: outerRadius * 0.3
                color: "#00ffff"
                antialiasing: true
            }
            Text {
                font.pointSize: 5
                id: speedLabel2
                anchors.top: speedLabel.bottom; anchors.left: speedLabel.left;
                text: rect.units
                font.pixelSize: outerRadius * 0.1
                color: "#00ffff"
                antialiasing: true
            }
        }


         tickmark: Rectangle {
            id: tick_big
            implicitWidth: outerRadius * 0.02
            implicitHeight: outerRadius * 0.06
            antialiasing: true
            smooth: true
            color: styleData.value <= gauge.value+gauge.tick_step ? "#00ffff" : "darkGray"
        }

        minorTickmark: Rectangle {
            id: tick_small
            implicitWidth: outerRadius * 0.01
            implicitHeight: outerRadius * 0.03

            antialiasing: true
            smooth: true
            color: styleData.value <= gauge.value+gauge.tick_step ? "#00ffff" : "darkGray"
        }

        tickmarkLabel:  Text {
            font.pixelSize: Math.max(10, outerRadius * 0.05)
            text: styleData.value
            color: styleData.value <= gauge.value ? "#00ffff" : "#777776"
            antialiasing: true
        }
        needle: Item {
            y: -outerRadius * 0.7
            height: outerRadius * 0.4
            Image {
                id: needle
                source: "resources/needle.svg"
                height: parent.height
                width: height * 0.3
                asynchronous: true
                antialiasing: true
            }

            Glow {
              anchors.fill: needle
              radius: 8
              samples: 10
              color: "#00badd"
              source: needle
          }
        }
        /*
         Canvas {
                property int value: gauge.value

                anchors.fill: parent
                onValueChanged: requestPaint()

                function degreesToRadians(degrees) {
                  return degrees * (Math.PI / 180);
                }

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();
                    ctx.beginPath();

                    ctx.strokeStyle = gauge.value < 25 ? "#4a17bf" : "#4a17ff"
                    ctx.lineWidth = outerRadius/6
                    ctx.arc(outerRadius,
                          outerRadius,
                          outerRadius - ctx.lineWidth / 2,
                          degreesToRadians(140),
                          degreesToRadians(valueToAngle(gauge.value)-90));
                    ctx.stroke();
                }
            }
            */

      }
 }
}
