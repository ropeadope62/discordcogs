import discord


class ReportEmbeds:
    def __init__(self, user, user_data):
        self.user = user
        self.user_data = user_data
        self.embed = discord.Embed(
            title="***Post Mortem®*** - brought to you by Slurm!:registered:",
            description="*Final Report Summary*",
            color=discord.Color.dark_red(),
        )

    # TODO Rename this here and in `report_embed` and `report_initial_embed`
    def report_embed(self):
        self.embed.set_author(
            name=self.user.display_name, icon_url=self.user.display_avatar.url
        )
        self.embed.add_field(name="Subject", value=self.user.mention, inline=False)
        self.embed.add_field(
            name="Death Progress",
            value=f"{self.user_data['progress_bar']} {self.user_data['progress'] * 100:.1f}%",
            inline=False,
        )
        self.embed.add_field(
            name="Subject Risk Factors",
            value=f"{self.user_data['risk_factor']}",
            inline=False,
        )
        self.embed.add_field(
            name="Approximate Age",
            value=f"{self.user_data['approximate_age']}",
            inline=False,
        )
        self.embed.add_field(
            name="Death Year",
            value=f"{self.user_data['death_year']}",
            inline=False,
        )
        self.embed.add_field(
            name="Approximate Death Age",
            value=f"{self.user_data['approximate_death_age']}",
            inline=False,
        )
        self.embed.add_field(
            name="Time Left",
            value=f"{self.user_data['years_left']} years... or {self.user_data['months_left']} months... or {self.user_data['weeks_left']} weeks... or {self.user_data['days_left']} days left to live.",
            inline=False,
        )
        self.embed.add_field(
            name="** Post Mortem® Likely result of death:**",
            value=f"*{self.user_data['cause_of_death']}*",
            inline=False,
        )
        self.embed.set_footer(text="\n Brought to you by Slurm!:tm:")
        return self.embed

    if __name__ == "__main__":
        # Test the embed_data function
        data = f"test data"
        print(report_embed(data))
