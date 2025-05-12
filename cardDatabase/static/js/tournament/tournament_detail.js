$(function () {
    let epoch = $('#startTime').data('epoch')
    if(!epoch){
        console.log('No start time given!')
        return;
    }   
    const startTime = epoch * 1000; // Convert to milliseconds

    function updateCountdown() {
        const now = new Date().getTime();
        const diff = startTime - now;
    
        if (diff <= 0) {
          document.getElementById("countdown").innerText = "Started";
          return;
        }
    
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
        document.getElementById("countdown").innerText =
          `${days}d ${hours}h ${minutes}m ${seconds}s`;
      }
    
      updateCountdown();
      setInterval(updateCountdown, 1000);
});