// A chat mark as the figure reads it: what the server guessed it is about when it wrote it, from its title, never matched again here
export class ChatMark {
    constructor(card) {
        this.card = card;
    }

    guessIsTest() {
        return Boolean(this.card.guesses?.test);
    }

    guessIsBuild() {
        return Boolean(this.card.guesses?.build);
    }

    guessIsUpload() {
        return Boolean(this.card.guesses?.upload);
    }
}
