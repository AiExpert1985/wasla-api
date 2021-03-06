var drivers;
var selected_drivers = [];

document.addEventListener('DOMContentLoaded', function(){
});

function initMap() {
    icon_base = "https://developers.google.com/maps/documentation/javascript/examples/full/images/";
    const map = new google.maps.Map(document.getElementById("map"), {
                                    zoom: 11,
                                    center: { lat: 36.3766596335, lng: 43.14640682224 },
                                    mapTypeId: "roadmap",
                                    });
    for(var i=0; i<selected_drivers.length; i++){
        var random_color = '#'+(0x1000000+(Math.random())*0xffffff).toString(16).substr(1,6);
        var path_coordinates = selected_drivers[i]["path"];
        var driver_path = new google.maps.Polyline({
                                path: path_coordinates,
                                geodesic: true,
                                strokeColor: random_color,
                                strokeOpacity: 2.0,
                                strokeWeight: 2.0,
                                });
        // show driver locations
        let driver_lat = selected_drivers[i]["coords"]["lat"];
        let driver_lng = selected_drivers[i]["coords"]["lng"];
        driver_lng = driver_lng + 0.0015* Math.random()
        let driver_marker = new google.maps.Marker({
                position: {"lat": driver_lat, "lng": driver_lng},
                map,
//                icon: "static/images/car_marker.png",
        });

        // display info when clicking driver icon
        const driver_info =
            '<div class="icon-info" dir="rtl">' +
                    '<h2 id="firstHeading" class="firstHeading">' + selected_drivers[i]['name'] + '</h1>' +
                    '<div id="bodyContent">' +
                        '<p dir="rtl"> الصفة : &nbsp سائق</p>' +
                        '<p dir="rtl"> المنطقة : &nbsp' + selected_drivers[i]['district'] + '</p>' +
                        '<p dir="rtl"> المسافة : &nbsp' + selected_drivers[i]['dist'] + ' &nbsp كم </p>' +
                        '<p dir="rtl"> هاتف : &nbsp' + selected_drivers[i]['phone'] + '</p>' +
                     "</div>" +
            "</div>";
        const driver_info_window = new google.maps.InfoWindow({
            content: driver_info,
          });
        driver_marker.addListener("click", () => {
            // remove previous info box - this was created by me ?
            info_div = document.querySelector(".icon-info");
            if (info_div != null){
                parent = info_div.parentNode.parentNode.parentNode.parentNode.parentNode;
                parent.remove();
            }
            driver_info_window.open({
              anchor: driver_marker,
              map,
              shouldFocus: false,
            });
         });
        // show student locations for each driver
        var students = selected_drivers[i].students;
        for(var j=0; j<students.length; j++){
            let student_lat = students[j]["coords"]["lat"];
            let student_lng = students[j]["coords"]["lng"];
            student_lat = student_lat + 0.0002* Math.random()
            student_lng = student_lng + 0.002* Math.random()
            let student_marker = new google.maps.Marker({
                                    position: {"lat": student_lat, "lng": student_lng},
                                    map,
                                    icon: icon_base + "library_maps.png",
                            });
            // display info when clicking student icon
            const student_info =
                '<div class="icon-info" dir="rtl">' +
                        '<h2 id="firstHeading" class="firstHeading">' + students[j]['name'] + '</h1>' +
                        '<div id="bodyContent">' +
                            '<p dir="rtl"> الصفة : &nbsp طالب</p>' +
                            '<p dir="rtl"> المنطقة : &nbsp' + students[j]['district'] + '</p>' +
                            '<p dir="rtl"> البوابة : &nbsp' + students[j]['gate_name'] + '</p>' +
                            '<p dir="rtl"> هاتف : &nbsp' + students[j]['phone'] + '</p>' +
                            '<p dir="rtl"> السائق : &nbsp' + students[j]['driver'] + '</p>' +
                         "</div>" +
                "</div>";
            const student_info_window = new google.maps.InfoWindow({
                content: student_info,
              });
            student_marker.addListener("click", () => {
                // remove previous info box - this was created by me ?
                info_div = document.querySelector(".icon-info");
                if (info_div != null){
                    parent = info_div.parentNode.parentNode.parentNode.parentNode.parentNode;
                    parent.remove();
                }
                student_info_window.open({
                  anchor: student_marker,
                  map,
                  shouldFocus: true,
                });
             });
        }
        driver_path.setMap(map)
    }
}

function add_stats(stats) {
    document.querySelector(".stats").hidden = false;
    var ids = ["#gate-stats", "#distance-stats", "#short-long-dist"];
    var groups = [['one_gate', 'two_gates', 'more_gates'],
                  ['total_distance', 'average_distance'],
                  ['shorted_distance', 'longest_distance']];
    for (var i = 0; i < ids.length; i++){
        var main_div = document.querySelector(ids[i]);
        for (var j=0; j<groups[i].length; j++){
            var key = groups[i][j];
            var div = document.createElement("div");
            div.innerHTML = stats[key];
            main_div.appendChild(div);
        }
    }
}

function add_drivers(){
    document.querySelector(".select-drivers").hidden = false;
    document.querySelector(".select-groups").hidden = false;
    document.querySelector(".save-button").hidden = false;
    document.querySelector(".all-drivers").checked = true;
    var main_div = document.querySelector(".select-drivers")
    for(var i = 0; i < drivers.length; i++){
        name = drivers[i]["name"];
        var div = document.createElement("div")
        main_div.appendChild(div)
        var label = document.createElement("label");
        label.innerHTML = name;
        var checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = name;
        checkbox.value = name;
        checkbox.name = name;
        checkbox.dataset.idx = i;
        checkbox.className += "select-driver";
        checkbox.checked = true;
        div.appendChild(checkbox);
        div.appendChild(label);
    }
}

document.querySelector('.select-drivers').addEventListener("change", (event)=> {
        let checkboxes = document.querySelectorAll(".select-driver");
        let num_checkboxes = checkboxes.length;
        let selections = [num_checkboxes]
        checkboxes.forEach(element => {
        let idx = element.dataset.idx
        let checked = element.checked;
        selections[idx] = checked;
    });
    selected_drivers = []
    for(var i=0; i<drivers.length; i++){
        if(selections[i] == true){
            selected_drivers.push(drivers[i]);
        }
    }
    initMap(selected_drivers);
    document.querySelector(".all-drivers").checked = false;
    if(selected_drivers.length == drivers.length){
        document.querySelector(".all-drivers").checked = true;
    }

});

document.querySelector('.select-groups').addEventListener("change", (event)=> {
    let is_all_drivers = document.querySelector(".all-drivers").checked;
    let checkboxes = document.querySelectorAll(".select-driver");
    if(is_all_drivers){
        selected_drivers = drivers;
        checkboxes.forEach(element => element.checked = true)
    }
    else {
        selected_drivers = [];
        checkboxes.forEach(element => element.checked = false);
    }
    initMap(selected_drivers);
});


let gates = true;
document.querySelector('#consider-gates').addEventListener("change", (event)=> gates = event.target.checked);

let drivers_file;
let input_drivers;
document.querySelector('#drivers').addEventListener("change", (event) => {
    drivers_file = event.target.files;
    let drivers_reader = new FileReader();
    drivers_reader.readAsBinaryString(drivers_file[0]);
    drivers_reader.onload = (event)=>{
        let drivers_data = event.target.result;
        let drivers_workbook = XLSX.read(drivers_data,{type:"binary"});
        let drivers_rowObject = XLSX.utils.sheet_to_row_object_array(drivers_workbook.Sheets[drivers_workbook.SheetNames[0]]);
        input_drivers = JSON.stringify(drivers_rowObject,undefined,4);
    }
});


let students_file;
let students;
document.querySelector('#students').addEventListener("change", (event) =>{
    students_file = event.target.files;
    let students_reader = new FileReader();
    students_reader.readAsBinaryString(students_file[0]);
    students_reader.onload = (event)=>{
        let students_data = event.target.result;
        let students_workbook = XLSX.read(students_data,{type:"binary"});
        let students_rowObject = XLSX.utils.sheet_to_row_object_array(students_workbook.Sheets[students_workbook.SheetNames[0]]);
        students = JSON.stringify(students_rowObject,undefined,4);
     }
});

document.querySelector('#post').addEventListener("click", () => {
    // first clear previous created elements if there are any
    let stats = document.querySelector(".stats");
    let children = stats.children;
    for(var i=0; i<children.length; i++){
        children[i].innerHTML = "";
    }
    document.querySelector(".select-drivers").innerHTML = "";
    // then start the fetch
    let data = {"drivers": input_drivers,
                "students": students,
                "consider_gates": gates,
                "api_key": "ksdjf34234a23423",
                "center_coords": [43.146406822212754, 36.37665963355008]
    };
    drivers = []
    selected_drivers = []
    fetch('/algorithm/data', {
      method: 'POST',
      headers: {
        'Content-Type': "application/json; charset=UTF-8"
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        stats = result['stats'];
        drivers = result['drivers'];
        selected_drivers = drivers;
        initMap(drivers);
        add_stats(stats);
        add_drivers(drivers);
     })
    .catch((error) => console.error('Error:', error));
});


// Below code related to saving results as excel file

function json_to_array(drivers){
    var drivers_arr = [];
    var column_titles = ["id", "name", "district", "x", "y", "leave_time", "gate_group", "gate_name",
                         "phone", "friends", "driver", "x", "y", "district", "dist", "duration", "phone"]
    drivers_arr.push(column_titles);
    for(var i=0; i<drivers.length; i++){
        var driver_name = drivers[i]["name"];
        var driver_coords = drivers[i]["coords"];
        var driver_distance = drivers[i]["dist"];
        var driver_district = drivers[i]["district"];
        var driver_phone = drivers[i]["phone"];
        var students = drivers[i]["students"];
        for(var j=0; j<4; j++){
            if(j >= students.length){drivers_arr.push([
                                      (i*4)+j+1,
                                      "","","","","","","","","",
                                      driver_name,
                                      driver_coords["lng"],
                                      driver_coords["lat"],
                                      driver_district,
                                      driver_distance,
                                      "",
                                      driver_phone,
                                      ]);
            }
            else{drivers_arr.push([
                              (i*4)+j+1,
                              students[j]["name"],
                              students[j]["district"],
                              students[j]["coords"]["lng"],
                              students[j]["coords"]["lat"],
                              "",
                              students[j]["gate_group"],
                              students[j]["gate_name"],
                              students[j]["phone"],
                              "",
                              driver_name,
                              driver_coords["lng"],
                              driver_coords["lat"],
                              driver_district,
                              driver_distance,
                              "",
                              driver_phone,
                              ]);
            }
        }
    }
    return(drivers_arr);
}

function s2ab(s) {
    var buf = new ArrayBuffer(s.length);
    var view = new Uint8Array(buf);
    for (var i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
    return buf;
}

function save_excel(){
    var wb = XLSX.utils.book_new();
    wb.SheetNames.push("Drivers");
	var drivers_arr = json_to_array(drivers);
    var ws = XLSX.utils.aoa_to_sheet(drivers_arr);
    wb.Sheets["Drivers"] = ws;
    var wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});
    saveAs(new Blob([s2ab(wbout)],{type:"application/octet-stream"}), 'Drivers.xlsx');
}

document.querySelector(".save-button").addEventListener("click", () => save_excel());
