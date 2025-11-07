<script lang="ts">
    export let title: string;
    export let subtitle: string;
</script>

<header class="chat-header">
    <h1>{title}</h1>
    <p>{subtitle}</p>
</header>

<style>
    .chat-header {
        padding: 20px 25px;
        border-bottom: 1px solid #eee;
        background-color: #e1e1fc59;
        flex-shrink: 0;
        text-align: center;
    }
    .chat-header h1 {
        margin: 0;
        font-size: 1.5rem;
        color: #333;
    }
    .chat-header p {
        margin: 0;
        color: #6a5af9;
        font-size: 0.9rem;
        padding: 0.5rem;
    }
    
    @media (max-width: 768px) {
        .chat-header {
            padding: 15px 20px;
        }
    }
</style>