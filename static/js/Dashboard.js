function ajaxCallOnFocusOut(obj,htmlElement){

            //console.log(JSON.stringify(obj))
            $.ajax({
                    type:'POST',
                    url: '/compare',
                    contentType:"application/json",
                    data: JSON.stringify(obj),
                    dataType: "json",
                    success:function(data){
                        //console.log(data," ")
                        if(data.error != null && data.error != undefined){
                                    htmlElement.closest(".form-group").find(".errorAlert").html(data.error)
                                    htmlElement.closest(".form-group").find(".errorAlert").css('display','block')
                                    htmlElement.closest(".form-group").find(".errorSuccess").css('display','none');
                            }
                        else if(data.success != null && data.success != undefined && data.success!=""){
                                htmlElement.closest(".form-group").find(".errorSuccess").html('Entered Accepted');
                                htmlElement.closest(".form-group").find(".errorSuccess").css('display','block');
                                htmlElement.closest(".form-group").find(".errorAlert").css('display','none')
                            }
                       }
            });
        }
        $(".formData").focusout(function(event) {
            var obj={}
            var key = $(this).attr("name")
            obj[key] = $(this).val()
            if($(this).val().length>1){
                //console.log(obj)
                ajaxCallOnFocusOut(obj,$(this))
            }
        })

//for updation
var ddthis
 $("#userDetails").on("click","#updateButton",function(){
       var tr=$(this).closest("tr").children();
          //console.log(tr);
          var empId=tr[0].innerHTML;
          var empName=tr[1].innerHTML;
          var projectId=$("#userDetails").dataTable().fnGetData(tr)[0];
          var employeeLevel=$("#userDetails").dataTable().fnGetData(tr)[3];
          var projectName=$("#userDetails").dataTable().fnGetData(tr)[4];
          var corpId=$("#userDetails").dataTable().fnGetData(tr)[7];
          var email=$("#userDetails").dataTable().fnGetData(tr)[6];
          var department=$("#userDetails").dataTable().fnGetData(tr)[5];
          var employeeStatus=$("#userDetails").dataTable().fnGetData(tr)[8];
          var expertise=$("#userDetails").dataTable().fnGetData(tr)[9];
          $("#exampleModal").modal("toggle");
          $("#empIdupdate").val(empId);
          $("#empName").val(empName);
          $("#pnupdate").val($.trim(projectName));
          $("#prismId").val(projectId);
          $("#corpIdUpdate").val(corpId);
          $("#emailIdUpdate").val(email);
          $("#DepartmentUpdate").val(department);
          $("#esupdate").val(employeeStatus);
          $("#expertiseUpdateId").val(expertise);
          $("#idEmployeeLevelUpdate").val(employeeLevel)
    });

    $("#userDetails").on("click","#deleteButton",function(){
        var tr=$(this).closest("tr").children();
        var empId=tr[0].innerHTML;
        var empName=tr[1].innerHTML;

        $('#deleteEmployeeId').text(empId);
        $('#deleteEmployeeName').text(empName);

        $('#deleteConfirmationModal').modal({
            show : true
        })
    });

$('#btnDeleteYes').click(function(){
    urlFinal = 'deleteEmployee'
    employeeId = $('#deleteEmployeeId')[0].innerHTML;
    $.ajax({
        url: '/' + urlFinal,
        type: 'GET',
        data: {
            'employeeId': employeeId
        },
        success: function (response) {
            if(response == 'employee deleted'){
                window.location = "/profile"
            }
        },
        error: function (jqXHR, error) {
            toastr.error("There was an error in deleting the employee")
        },
        complete: function () {
        }
    })
});

function jsonDataForProjectDetails(){
    $.ajax({
        dataType:'json',
        url:"/dj",
        type:'get',
        success:function(data){
            var projectName=[]
            //console.log(data["project details"][1]["projectId"])
            for (var i = 0;i<data["project details"].length;i++)
            {
                projectName[i]=data["project details"][i]["projectName"]
//                console.log(projectName[i])
                if(ddthis == projectName[i]){
//                    console.log(ddthis)
                    $('.ProjectID').val(data["project details"][i]["projectId"])
                    $('.Department').val(data["project details"][i]["department"])
                    break
                }
            }
        },
        error:function(error){
            alert(error)
        }
    })
}

//main
$(document).ready(function(){

        $("#register").click(function(){
             $(".alert").hide();
        });

        });
