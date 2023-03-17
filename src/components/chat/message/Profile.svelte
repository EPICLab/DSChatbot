<script type="ts">
  import Person from "../../icons/person.svelte";
  import Robot from "../../icons/robot.svelte";

  export let type: string = "user";
  export let title: string = "You";

</script>


<div class="profile {type}">
  {#if type == "user"} 
    <div class="profile-inner" {title}>
      <Person/>
    </div>
  {:else}
    <div class="profile-inner" {title}>
      <Robot/>
    </div>
  {/if}
</div>

<style>

  .profile{
    height:25px;
    width:25px;
    position:relative;
    overflow:hidden;
  }

  .bot.profile, .error.profile {
    border-right: 1px solid black;
  }

  .user.profile {
    border-left: 1px solid black;
  }
    
  .profile-inner {
    background-color: white;
    
    border-radius:50%;
    height:20px;
    width:20px;
    overflow:hidden;

    position:absolute;
    left:50%;
    top:50%;
    -webkit-transform:translateX(-50%) translateY(-50%);
    transform:translateX(-50%) translateY(-50%);
  }

  .user .profile-inner {
    border: 15px solid var(--newton-message-user-color);
  }

  .bot .profile-inner{
    border: 15px solid var(--newton-message-bot-color);
  }

  .error .profile-inner{
    border: 15px solid var(--newton-message-error-color);
  }

</style>