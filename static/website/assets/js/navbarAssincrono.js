

   function som() {
    var audio = new Audio("{% static 'website/assets/mp3/som.mp3' %}");
    audio.play();
    
  }

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  $(document).ready(function() {
    
    var csrftoken = getCookie('csrftoken');
    var notificationTable = $('.notification-table');
    notificationTable.hide();

    var numeroNotificacoes = localStorage.getItem('numeroNotificacoes');
    if (numeroNotificacoes) {
      $('#bolinha-vermelha').text(numeroNotificacoes);
    }

    var a = parseInt(localStorage.getItem('a')) || 0;

    function loadNotifications() {
      
      var notificationBody = notificationTable.find('.notification-body');
      notificationBody.empty();

      $.ajax({
        url: '/notificacoes/{{ request.user.username }}',
        type: 'GET',
        dataType: 'json',
        beforeSend: function(xhr) {
          xhr.setRequestHeader('X-CSRFToken', csrftoken);
        },
        success: function(data) {
          var notifications = data.notifications;
          if (notifications.length === 0) {
            var notificationRow = $('<tr class="notification-row"><td class="notification-item">Nenhuma notificação de momento</td></tr>');
            notificationBody.append(notificationRow);
          } else {
            for (var i = 0; i < notifications.length; i++) {
              var notification = notifications[i];
              var message = notification.message;
              var notificationRow = $('<tr class="notification-row"></tr>').attr('data-id', notification.id);
              var notificationItem = $('<td class="notification-item"></td>').text(message);
              notificationRow.append(notificationItem);
              if (notifications.length > 0) {
                if (i === 0) {
                  var new2 = $('<td class="notification-novas">Notificações sobre encomendas suas:</td>');
                  notificationBody.append(new2);
                 
                  
                  
                  
                }
                notificationBody.append(notificationRow);

              
            }
            
          }
            var br = $('<br>');
            notificationBody.append(br);

            var dele = $('<button class="delete-notifications btn btn-danger btn-sm">Delete All</button>');
            notificationBody.append(dele);

            dele.click(function() {
              $.ajax({
                url: '/delete-notifications/{{ request.user.username }}',
                type: 'POST',
                dataType: 'json',
                beforeSend: function(xhr) {
                  xhr.setRequestHeader('X-CSRFToken', csrftoken);
                },
                success: function(response) {
                  notificationBody.find('.notification-row').remove();
                  notificationBody.find('.notification-novas').remove();
                  notificationBody.find('.delete-notifications').remove();

                  $('#bolinha-vermelha').text(0);
                  localStorage.setItem('numeroNotificacoes', 0);
                  localStorage.setItem('a', 0);

                  loadNotifications();
                },
                error: function(xhr, status, error) {
                  console.log(error);
                }
              });
            });
          }

          var novoNumeroNotificacoes = data.numeroNotificacoes;
          $('#bolinha-vermelha').text(novoNumeroNotificacoes);
          localStorage.setItem('numeroNotificacoes', novoNumeroNotificacoes);
          localStorage.setItem('a', notifications.length);
          
        },
        error: function(xhr, status, error) {
          console.log(error);
        },
        complete: function() {
          setTimeout(loadNotifications, 10000);
        }
      });
    }

    loadNotifications();

    $('.notification-icon').click(function() {
      if (notificationTable.is(':visible')) {
        notificationTable.hide();
      } else {
        notificationTable.show();
      }
    });
  });