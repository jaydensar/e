import { PrismaClient } from "@prisma/client";
import express from "express";

const prisma = new PrismaClient();

const app = express();

app.use(express.json());

app.get("/user-exists/:username", async (req, res) => {
  const user = await prisma.user.findUnique({
    where: {
      name: req.params.username,
    },
    rejectOnNotFound: false,
  });

  if (!user) {
    return res.sendStatus(204);
  }

  return res.sendStatus(200);
});

app.post("/register", async (req, res) => {
  try {
    const udata = await prisma.user.create({
      data: {
        name: req.body.name,
        guilds: {
          create: {
            name: (req.body.name as string) + "'s server",
          },
        },
      },
      include: {
        guilds: true,
      },
    });

    await prisma.channel.create({
      data: {
        name: "general",
        guildId: udata.guilds[0].id,
      },
    });

    res.sendStatus(200);
  } catch (e) {
    res.sendStatus(500);
  }
});

app.get("/guilds/:name", async (req, res) => {
  const guilds = await prisma.user
    .findUnique({
      where: {
        name: req.params.name,
      },
    })
    .guilds({
      include: {
        channels: true,
      },
    });

  try {
    res.status(200).json({ data: guilds });
  } catch (e) {
    res.sendStatus(500);
  }
});

app.post("/message", (req, res) => {});

app.listen(3000, () => {
  console.log(`Listening on port ${process.env.PORT}`);
});
