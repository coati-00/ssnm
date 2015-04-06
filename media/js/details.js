$(document).ready(function () {

    var txt = false;
    var otxt = false;


    $("form").submit(
      function(e)
      {

        if(!($("#id_name").val()) && txt == false)
          {
              $("#id_name").after('<p id="par" style="color:red">Please enter a name for your map to continue.</p>');
              txt = true;
              e.preventDefault();
          }

        if(($("#id_description").val().length > 500) && otxt == false)
          {
              $("#id_description").after('<p id="par" style="color:red">This description is too long, please make it shorter.</p>');
              otxt = true;
              e.preventDefault();
          }


      });
   
})
        

 