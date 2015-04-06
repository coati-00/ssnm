    function confirmation(map) {
        var current = location.href;
        var link = map.substring(1);
        var redirect = current + link;
        var answer = confirm("Are you sure you want to delete this map?")
        if (answer){
            window.location = redirect;
        }
    }