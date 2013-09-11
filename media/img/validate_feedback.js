function validate(){

      var emptyString = /^\s*$/
      var errs=0;

      if (emptyString.test(document.forms.feedback.email.value)) errs += 1; 
      if (emptyString.test(document.forms.feedback.name.value)) errs += 1; 
      if (emptyString.test(document.forms.feedback.description.value)) errs += 1; 

      if (errs>0) alert('Please fill out all the information in the form');

      return (errs==0);

};